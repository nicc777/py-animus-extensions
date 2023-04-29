
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

        try:        
            client = boto3_session.client('s3')
            response = client.head_bucket(
                Bucket='string',
                ExpectedBucketOwner='string'
            )
            self.log(message='response={}'.format(json.dumps(response)), level='debug')
        except:
            self.log(message='EXCEPTION: {}'.format(traceback.format_exc()), level='error')
            return True

        return False

    def _set_variables(self, exists: bool=True, variable_cache: VariableCache=VariableCache(), target_environment: str='default'):
        variable_cache.store_variable(
            variable=Variable(
                name='{}:BUCKET_EXISTS'.format(self._var_name(target_environment=target_environment)),
                initial_value=exists,
                logger=self.logger
            ),
            overwrite_existing=True
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:NAME'.format(self._var_name(target_environment=target_environment)),
                initial_value=copy.deepcopy(self.spec['name']),
                logger=self.logger
            ),
            overwrite_existing=True
        )

    def _add_parameter(self, spec_param_name: str, boto3_param_name: str, current_parameters: dict=dict(), type_def: object=str)->dict:
        if spec_param_name in self.spec:
            if self.spec[spec_param_name] is not None:
                if isinstance(self.spec[spec_param_name], type_def) is True:
                    current_parameters[boto3_param_name] = self.spec[spec_param_name]
        return copy.deepcopy(current_parameters)

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='APPLY CALLED', level='info')

        if self.implemented_manifest_differ_from_this_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache, target_environment=target_environment, value_placeholders=value_placeholders) is False:
            self.log(message='    Bucket "{}" already appears to exist for environment "{}"'.format(self.spec['name'], target_environment), level='info')
            self._set_variables(exists=True, variable_cache=variable_cache, target_environment=target_environment)
            return
        
        parameters = dict()
        parameters['Bucket'] = self.spec['name']
        parameters = self._add_parameter(spec_param_name='acl', boto3_param_name='ACL', current_parameters=copy.deepcopy(parameters), type_def=str)
        parameters = self._add_parameter(spec_param_name='grantFullControl', boto3_param_name='GrantFullControl', current_parameters=copy.deepcopy(parameters), type_def=str)
        parameters = self._add_parameter(spec_param_name='grantRead', boto3_param_name='GrantRead', current_parameters=copy.deepcopy(parameters), type_def=str)
        parameters = self._add_parameter(spec_param_name='grantReadACP', boto3_param_name='GrantReadACP', current_parameters=copy.deepcopy(parameters), type_def=str)
        parameters = self._add_parameter(spec_param_name='grantWrite', boto3_param_name='GrantWrite', current_parameters=copy.deepcopy(parameters), type_def=str)
        parameters = self._add_parameter(spec_param_name='grantWriteACP', boto3_param_name='GrantWriteACP', current_parameters=copy.deepcopy(parameters), type_def=str)
        parameters = self._add_parameter(spec_param_name='objectLockEnabledForBucket', boto3_param_name='ObjectLockEnabledForBucket', current_parameters=copy.deepcopy(parameters), type_def=bool)
        parameters = self._add_parameter(spec_param_name='objectOwnership', boto3_param_name='ObjectOwnership', current_parameters=copy.deepcopy(parameters), type_def=str)

        boto3_session_base_name = 'AwsBoto3Session:{}:{}'.format(
            self.spec['awsBoto3Session'],
            target_environment
        )
        boto3_session = variable_cache.get_value(
            variable_name='{}:SESSION'.format(boto3_session_base_name),
            value_if_expired=False,
            default_value_if_not_found=False,
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )

        try:        
            client = boto3_session.client('s3')
            response = client.create_bucket(**parameters)
            self.log(message='response={}'.format(json.dumps(response)), level='debug')
            self._set_variables(exists=True, variable_cache=variable_cache, target_environment=target_environment)
        except:
            self.log(message='EXCEPTION: {}'.format(traceback.format_exc()), level='error')
            self._set_variables(exists=False, variable_cache=variable_cache, target_environment=target_environment)

        return 
    
    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='DELETE CALLED', level='info')
        return 
