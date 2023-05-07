import traceback
import boto3
import os
import shutil
import tempfile
from pathlib import Path
import re
import hashlib
from py_animus.manifest_management import *
from py_animus import get_logger
from py_animus.file_io import *


class AwsBoto3S3Files(ManifestBase):
    """Synchronizes files to an S3 bucket (apply action) or deletes the files in an S3 bucket (delete action).

It is important that the bucket remain under control of Animus (both through `AwsBoto3S3Bucket` amd `AwsBoto3S3Files`)
to avoid inconsistencies or loss of dat or data corruption.

The intent of this facility is to keep file synchronized that are required for IaC activities. Ir was not really meant
for uploading or synchronizing a large amount of files. Consider using the AWS CLI tool 
[aws s3 sync](https://docs.aws.amazon.com/cli/latest/reference/s3/sync.html) for bulk file uploads (1000+ files)

When the apply action is complete the following variable will be set:

* `:SYNC_RESULT` - Set to the string `ALL_OK`` when done.
* `:CHECKSUM_DIFFERENCES_DETECTED` - Boolean value which will only be present if some files or directories had the `verifyChecksums` parameter set to `true`. If this variable is `true`, it means some of the files evaluated did have a mismatch in checksum and was re-uploaded. If the `verifyChecksums` parameter was never used, this variable may be absent or have a value of `False`

Both individual files, or entire directory contents can be uploaded.

There are several strategies that can be followed: 

* Ignore the current files in the bucket, and just overwrite all of them
* A longer process can first get the checksum of each remote file and compare it with the local file and only upload the differences.

Restrictions:

* Please be aware of file and directory (a.k.a. "key") [naming conventions and restriction](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html) for S3.
* Be aware of the AWS S3 [service quotas](https://docs.aws.amazon.com/general/latest/gr/s3.html)
* It is encouraged to re-use the same `AwsBoto3Session` that was used to create the S3 bucket. This will avoid potential issues with end-point usage etc.

    """    

    def __init__(self, logger=get_logger(), post_parsing_method: object=None, version: str='v1', supported_versions: tuple=(['v1'])):
        super().__init__(logger=logger, post_parsing_method=post_parsing_method, version=version, supported_versions=supported_versions)

    def _var_name(self, target_environment: str='default'):
        return '{}:{}:{}'.format(
            self.__class__.__name__,
            self.metadata['name'],
            target_environment
        )

    def _get_boto3_s3_client(self, variable_cache: VariableCache=VariableCache(), target_environment: str='default'):
        boto3_session_base_name = 'AwsBoto3Session:{}:{}'.format(
            self.spec['awsBoto3Session'],
            target_environment
        )
        if variable_cache.get_value(
            variable_name='{}:CONNECTED'.format(boto3_session_base_name),
            value_if_expired=False,
            default_value_if_not_found=False,
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        ) is False:
            raise Exception('Boto3 Session Does not exist or is not connected yet. Ensure a Boto3 Session is a dependant of this manifest and that the environments match.')
        
        boto3_session = variable_cache.get_value(
            variable_name='{}:SESSION'.format(boto3_session_base_name),
            value_if_expired=False,
            default_value_if_not_found=False,
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        if boto3_session:
            return boto3_session.client('s3')
        raise Exception('Unable to create S3 client')
    
    def _set_variables(self, all_ok: bool=True, checksum_differences_detected: bool=False, variable_cache: VariableCache=VariableCache(), target_environment: str='default'):
        result_txt = 'ALL_OK'
        if all_ok is False:
            result_txt = 'NOT_OK'
        variable_cache.store_variable(
            variable=Variable(
                name='{}:SYNC_RESULT'.format(self._var_name(target_environment=target_environment)),
                initial_value=result_txt,
                logger=self.logger
            ),
            overwrite_existing=True
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:CHECKSUM_DIFFERENCES_DETECTED'.format(self._var_name(target_environment=target_environment)),
                initial_value=checksum_differences_detected,
                logger=self.logger
            ),
            overwrite_existing=True
        )

    def _get_bucket_name(self, variable_cache: VariableCache=VariableCache(), target_environment: str='default')->str:
        bucket_name = variable_cache.get_value(
            variable_name='AwsBoto3S3Bucket:{}:{}:NAME'.format(self.spec['s3Bucket'], target_environment),
            value_if_expired=None,
            default_value_if_not_found=None,
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        if bucket_name is not None:
            if isinstance(bucket_name, str):
                if len(bucket_name) > 0:
                    return bucket_name
        raise Exception('Bucket name not found')
    
    def _bucket_exists(self, variable_cache: VariableCache=VariableCache(), target_environment: str='default')->bool:
        try:        
            client = self._get_boto3_s3_client(variable_cache=variable_cache, target_environment=target_environment)
            response = client.head_bucket(
                Bucket=self._get_bucket_name(variable_cache=variable_cache, target_environment=target_environment)
            )
            self.log(message='response={}'.format(json.dumps(response, default=str)), level='debug')
            return True
        except:
            self.log(message='EXCEPTION: {}'.format(traceback.format_exc()), level='error')
        return False

    def _get_all_s3_keys(self, variable_cache: VariableCache=VariableCache(), target_environment: str='default', continuation_token: str=None, start_after: str=None)->dict:
        keys = dict()
        try:
            client = self._get_boto3_s3_client(variable_cache=variable_cache, target_environment=target_environment)
            response = None
            if continuation_token is not None:
                if start_after is not None:
                    response = client.list_objects_v2(
                        Bucket=self._get_bucket_name(variable_cache=variable_cache, target_environment=target_environment),
                        MaxKeys=100,
                        ContinuationToken=continuation_token,
                        StartAfter=start_after
                    )
                else:
                    response = client.list_objects_v2(
                        Bucket=self._get_bucket_name(variable_cache=variable_cache, target_environment=target_environment),
                        MaxKeys=100,
                        ContinuationToken=continuation_token
                    )
            else:
                response = client.list_objects_v2(
                    Bucket=self._get_bucket_name(variable_cache=variable_cache, target_environment=target_environment),
                    MaxKeys=100
                )
            if 'ContinuationToken' in response:
                new_continuation_token = response['ContinuationToken']
                new_start_after = None
                if 'StartAfter' in response:
                    new_start_after = response['StartAfter']
                keys = {**keys, **self._get_all_s3_keys(variable_cache=variable_cache, target_environment=target_environment, continuation_token=new_continuation_token, start_after=new_start_after)}
            if 'Contents' in response:
                for key_data in response['Contents']:
                    key_checksum = hashlib.sha256(key_data['Key'].encode('utf-8')).hexdigest()
                    keys[key_checksum] = dict()
                    keys[key_checksum]['Key'] = key_data['Key']
                    keys[key_checksum]['Size'] = key_data['Size']
                    keys[key_checksum]['ContentChecksumSha256'] = None
        except:
            self.log(message='EXCEPTION: {}'.format(traceback.format_exc()), level='error')
        return keys

    def _delete_s3_key(self, key: str, variable_cache: VariableCache=VariableCache(), target_environment: str='default'):
        try:
            client = self._get_boto3_s3_client(variable_cache=variable_cache, target_environment=target_environment)
            client.delete_object(
                Bucket=self._get_bucket_name(variable_cache=variable_cache, target_environment=target_environment),
                Key=key
            )
        except:
            self.log(message='EXCEPTION: {}'.format(traceback.format_exc()), level='error')

    def _retrieve_local_file_meta_data(self, base_directory: str, file_name_portion: str, verify_checksums: bool=False)->dict:
        result = dict()
        file_full_path = '{}{}{}'.format(base_directory, os.sep, file_name_portion)
        self.log(message='Attempting to add file "{}"'.format(file_full_path), level='info')
        file_size = get_file_size(file_path=file_full_path)
        if file_size is not None:
            result['Key'] = file_name_portion
            result['LocalFullPath'] = file_full_path
            result['BaseDirectory'] = base_directory
            result['Size'] = file_size
            result['ContentChecksumSha256'] = calculate_file_checksum(file_path=file_full_path, checksum_algorithm='sha256', _known_size=file_size)
            result['VerifyS3Checksum'] = verify_checksums
        else:
            self.log(message='Failed to get filesize for file "{}" - skipping file. Please ensure it exists.'.format(file_full_path), level='warning')
            return None
        return result

    def _get_all_local_files(self, variable_cache: VariableCache=VariableCache(), target_environment: str='default')->dict:
        files = dict()
        if 'sources' in self.spec:
            for source_definition in self.spec['sources']:
                if 'sourceType' in source_definition and 'baseDirectory' in source_definition:
                    verify_checksums = False
                    base_directory = source_definition['baseDirectory']
                    if 'verifyChecksums' in source_definition:
                        verify_checksums = source_definition['verifyChecksums']
                    if source_definition['sourceType'].lower() == 'localfiles':
                        if 'files' in source_definition:
                            for file_name in source_definition['files']:
                                file_full_path = '{}{}{}'.format(base_directory, os.sep, file_name)
                                self.log(message='Attempting to add file "{}"'.format(file_full_path), level='info')
                                target_key_checksum = hashlib.sha256(file_name.encode('utf-8')).hexdigest()
                                local_file_metadata = self._retrieve_local_file_meta_data(base_directory=base_directory, file_name_portion=file_name, verify_checksums=verify_checksums)
                                if local_file_metadata is not None:                                    
                                    files[target_key_checksum] = local_file_metadata
                        else:
                            self.log(message='No actual files found. Ignoring this section: Problematic source_definition={}'.format(json.dumps(source_definition)), level='warning')
                    elif source_definition['sourceType'].lower() == 'localdirectories':
                        recurse = False
                        if 'recurse' in source_definition:
                            recurse = source_definition['recurse']
                        if 'verifyChecksums' in source_definition:
                            verify_checksums = source_definition['verifyChecksums']
                        directory_list = list()
                        if 'directories' in source_definition:
                            for dir in source_definition['directories']:
                                directory_list.append('{}{}{}'.format(base_directory, os.sep, dir))
                        else:
                            directory_list.append(base_directory)
                        for dir in directory_list:
                            file_list_data = list_files(directory=dir, recurse=recurse)
                            for file_full_path in list(file_list_data.keys()):
                                full_base_dir = '{}{}'.format(base_directory, os.sep)
                                file_name = copy.deepcopy(file_full_path).replace(full_base_dir, '')
                                self.log(message='Attempting to add file "{}"'.format(file_full_path), level='info')
                                target_key_checksum = hashlib.sha256(file_name.encode('utf-8')).hexdigest()
                                local_file_metadata = self._retrieve_local_file_meta_data(base_directory=base_directory, file_name_portion=file_name, verify_checksums=verify_checksums)
                                if local_file_metadata is not None:                                    
                                    files[target_key_checksum] = local_file_metadata
                    else:
                        self.log(message='Unsupported source type "{}" SKIPPED'.format(source_definition['sourceType']), level='warning')
                else:
                    self.log(message='Not all required fields present. Problematic source_definition={}'.format(json.dumps(source_definition)), level='warning')
        else:
            self.log(message='NO SOURCES found in Spec - Nothing to do', level='warning')
        return files

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders())->bool:
        if target_environment not in self.metadata['environments']:
            return False
        
        s3_keys = self._get_all_s3_keys(variable_cache=variable_cache, target_environment=target_environment)
        local_files = self._get_all_local_files(variable_cache=variable_cache, target_environment=target_environment)

        self.log(message='s3_keys={}'.format(json.dumps(s3_keys)), level='debug')
        self.log(message='local_files={}'.format(json.dumps(local_files)), level='debug')

        return False

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='APPLY CALLED', level='info')

        if self._bucket_exists(variable_cache=variable_cache, target_environment=target_environment) is False:
            raise Exception('Bucket does not exist - cannot continue')

        if self.implemented_manifest_differ_from_this_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache, target_environment=target_environment, value_placeholders=value_placeholders) is False:
            self.log(message='    Bucket "{}" in environment "{}" already appears to be synchronized'.format(self._get_bucket_name(variable_cache=variable_cache, target_environment=target_environment), target_environment), level='info')
            self._set_variables(all_ok=True, checksum_differences_detected=False, variable_cache=variable_cache, target_environment=target_environment)
            return

        return 
    
    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        if self._bucket_exists(variable_cache=variable_cache, target_environment=target_environment) is False:
            self.log(message='Bucket already deleted', level='warning')
        s3_keys = self._get_all_s3_keys(variable_cache=variable_cache, target_environment=target_environment)
        for key_hash, key_data in s3_keys.items():
            self._delete_s3_key(key=key_data['Key'], variable_cache=variable_cache, target_environment=target_environment)
            self.log(message='   Deleted known S3 key "{}"'.format(key_data['Key']), level='info')   
        # TODO Delete temporary files
        # TODO Delete temporary work directories 
        self.log(message='DELETE CALLED', level='info')
        return 
