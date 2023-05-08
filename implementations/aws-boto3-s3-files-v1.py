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

    def _download_s3_key(self, key: str, work_dir: str, variable_cache: VariableCache=VariableCache(), target_environment: str='default')->str:
        local_file_name = hashlib.sha256(key.encode('utf-8')).hexdigest()
        saved_file_path = '{}{}{}'.format(work_dir, os.sep, local_file_name)
        try:
            client = self._get_boto3_s3_client(variable_cache=variable_cache, target_environment=target_environment)
            with open(saved_file_path, 'wb') as f:
                client.download_fileobj(self._get_bucket_name(variable_cache=variable_cache, target_environment=target_environment), key, f)
            self.log(message='Downloaded S3 key "{}" to local file "{}"'.format(key, saved_file_path), level='info')
        except:
            self.log(message='EXCEPTION: {}'.format(traceback.format_exc()), level='error')
            return None
        return saved_file_path

    def _files_to_transfer(self, current_s3_keys: dict, local_files: dict, work_dir: str, variable_cache: VariableCache=VariableCache(), target_environment: str='default')->dict:
        files_to_transfer = dict()
        for local_key, key_data in local_files.items():
            if local_key not in current_s3_keys:
                files_to_transfer[local_key] = copy.deepcopy(key_data)
                self.log(message='Local file "{}" not found in S3 - marked for UPLOAD'.format(key_data['LocalFullPath']), level='info')
            else:
                if 'VerifyS3Checksum' in key_data and 'ContentChecksumSha256' in key_data:
                    if key_data['VerifyS3Checksum'] is True:
                        downloaded_file_path = self._download_s3_key(key=current_s3_keys[local_key]['Key'], work_dir=work_dir, variable_cache=variable_cache, target_environment=target_environment)
                        downloaded_file_checksum = calculate_file_checksum(file_path=downloaded_file_path, checksum_algorithm='sha256')
                        if key_data['ContentChecksumSha256'] != downloaded_file_checksum:
                            files_to_transfer[local_key] = copy.deepcopy(key_data)
                            self.log(message='Local file "{}" found in S3 and checksums mismatch - marked for UPLOAD'.format(key_data['LocalFullPath']), level='info')
                        else:
                            if 'ifFileExists' in self.spec:
                                if self.spec['ifFileExists']['overWrite'] is True:
                                    files_to_transfer[local_key] = copy.deepcopy(key_data)
                                    self.log(message='Local file "{}" marked for UPLOAD ("ifFileExists" is set to "{}")'.format(key_data['LocalFullPath'], self.spec['ifFileExists']['overWrite']), level='info')
                                else:
                                    self.log(message='Local file "{}" found in S3 and checksums match - ignoring file ("ifFileExists" is set to "{}")'.format(key_data['LocalFullPath'], self.spec['ifFileExists']['overWrite']), level='info')
                            else:
                                self.log(message='Local file "{}" found in S3 and checksums match - ignoring file'.format(key_data['LocalFullPath']), level='info')
                    else:
                        if 'ifFileExists' in self.spec:
                            if self.spec['ifFileExists']['overWrite'] is True:
                                files_to_transfer[local_key] = copy.deepcopy(key_data)
                                self.log(message='Local file "{}" marked for UPLOAD ("ifFileExists" is set to "{}")'.format(key_data['LocalFullPath'], self.spec['ifFileExists']['overWrite']), level='info')
                            else:
                                self.log(message='Local file "{}" found in S3 and checksums match - ignoring file ("ifFileExists" is set to "{}")'.format(key_data['LocalFullPath'], self.spec['ifFileExists']['overWrite']), level='info')
                        else:
                            self.log(message='Local file "{}" found in S3 - ignoring file'.format(key_data['LocalFullPath']), level='info')
        return files_to_transfer
    
    def _remote_files_to_delete(self, current_s3_keys: dict, local_files: dict, work_dir: str, variable_cache: VariableCache=VariableCache(), target_environment: str='default')->dict:
        files_to_delete = dict()
        if 'actionExtraFilesOnS3' in self.spec:
            if self.spec['actionExtraFilesOnS3'].lower() == 'keep':
                self.log(message='All remote keys will be kept as "actionExtraFilesOnS3" is set to "{}"'.format(self.spec['actionExtraFilesOnS3'].lower()), level='info')
                return files_to_delete
        for remote_key, remote_key_data in current_s3_keys.items():
            if remote_key not in local_files:
                files_to_delete[remote_key] = copy.deepcopy(remote_key_data)
                self.log(message='Remote key "{}" will be deleted (not found in local files collection)'.format(remote_key_data['Key']), level='info')
        return files_to_delete

    def _create_temporary_working_directory(self)->str:
        work_dir = ''
        if 'localStagingDirectory' in self.spec:
            work_dir = self.spec['localStagingDirectory']
            create_directory(path=work_dir)
        else:
            work_dir = create_temp_directory()
        return work_dir

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders())->bool:
        if target_environment not in self.metadata['environments']:
            return False
        
        work_dir = self._create_temporary_working_directory()

        s3_keys = self._get_all_s3_keys(variable_cache=variable_cache, target_environment=target_environment)
        local_files = self._get_all_local_files(variable_cache=variable_cache, target_environment=target_environment)
        files_to_transfer = self._files_to_transfer(current_s3_keys=s3_keys, local_files=local_files, work_dir=work_dir, variable_cache=variable_cache, target_environment=target_environment)
        files_to_delete = self._remote_files_to_delete(current_s3_keys=s3_keys, local_files=local_files, work_dir=work_dir, variable_cache=variable_cache, target_environment=target_environment)

        self.log(message='{}'.format('*'*80), level='debug')
        self.log(message='s3_keys            = {}'.format(json.dumps(s3_keys)), level='debug')
        self.log(message='{}'.format('*'*80), level='debug')
        self.log(message='local_files        = {}'.format(json.dumps(local_files)), level='debug')
        self.log(message='{}'.format('*'*80), level='debug')
        self.log(message='files_to_transfer  = {}'.format(json.dumps(files_to_transfer)), level='debug')
        self.log(message='{}'.format('*'*80), level='debug')
        self.log(message='files_to_delete  = {}'.format(json.dumps(files_to_delete)), level='debug')
        self.log(message='{}'.format('*'*80), level='debug')

        if work_dir != tempfile.gettempdir():   # Do not delete the system default temp directory if that was the directory set as the work dir
            delete_directory(dir=work_dir)

        variable_cache.store_variable(
            variable=Variable(
                name='{}:FILES_TO_TRANSFER'.format(self._var_name),
                initial_value=files_to_transfer
            ),
            overwrite_existing=True
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:FILES_TO_DELETE'.format(self._var_name),
                initial_value=files_to_delete
            ),
            overwrite_existing=True
        )

        if len(files_to_transfer) > 0 or len(files_to_delete) > 0:
            return True

        return False
    
    def _upload_local_file(self, local_file_path: str, target_key: str, variable_cache: VariableCache=VariableCache(), target_environment: str='default'):
        try:
            client = self._get_boto3_s3_client(variable_cache=variable_cache, target_environment=target_environment)
            with open(local_file_path, 'rb') as f:
                client.upload_fileobj(f, self._get_bucket_name(variable_cache=variable_cache, target_environment=target_environment), target_key)
            self.log(
                message='Uploaded local file "{}" to S3 key "s3://{}/{}"'.format(
                    local_file_path,
                    self._get_bucket_name(variable_cache=variable_cache, target_environment=target_environment),
                    target_key
                ),
                level='info'
            )
        except:
            self.log(message='EXCEPTION: {}'.format(traceback.format_exc()), level='error')

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

        files_to_transfer = variable_cache.get_value(
            variable_name='{}:FILES_TO_TRANSFER'.format(self._var_name),
            value_if_expired=dict(),
            default_value_if_not_found=dict(),
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        files_to_delete = variable_cache.get_value(
            variable_name='{}:FILES_TO_DELETE'.format(self._var_name),
            value_if_expired=dict(),
            default_value_if_not_found=dict(),
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )

        for local_key, local_key_data in files_to_transfer.items():
            self._upload_local_file(
                local_file_path=local_key_data['LocalFullPath'],
                target_key=local_key_data['Key'],
                variable_cache=variable_cache,
                target_environment=target_environment
            )
        for remote_key, remote_key_data in files_to_delete.items():
            self._delete_s3_key(
                key=remote_key_data['Key'],
                variable_cache=variable_cache,
                target_environment=target_environment
            )

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
