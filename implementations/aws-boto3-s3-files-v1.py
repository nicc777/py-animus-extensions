
from py_animus.manifest_management import *
from py_animus import get_logger
import traceback
import boto3
import os
import shutil
import tempfile
from pathlib import Path
import re
import hashlib




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

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders())->bool:
        if target_environment not in self.metadata['environments']:
            return False
        return False

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='APPLY CALLED', level='info')
        return 
    
    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='DELETE CALLED', level='info')
        return 
