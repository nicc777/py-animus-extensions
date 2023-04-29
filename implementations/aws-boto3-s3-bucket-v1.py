
from py_animus.manifest_management import *
from py_animus import get_logger
import traceback
import boto3




class AwsBoto3S3Bucket(ManifestBase):
    """Manages an S3 bucket. Version aims to support the following features:

* Create a new bucket with the `apply` action
* Delete an existing bucket with the `delete` action that was created earlier with the apply action
    * If the bucket is not empty, the delete behavior will have three options: a) Ignore the delete and just carry on; b) Delete all content, and then delete the bucket; and c) Stop with an error/Exception
* A lot of the supported boto3 options can be set, but in v1 changes to these settings can not yet be handled (planned for a future version). This, for example, applies to changing the ACL or object ownership settings.

Using this manifest depends on `AwsBoto3Session` and will need a dependency for a session manifest.

Since the introduction of environments and variables, it will be possible to use one manifest for buckets in different accounts, assuming at least one AWS account per environment.

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
