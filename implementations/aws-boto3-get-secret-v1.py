from py_animus.manifest_management import *
from py_animus import get_logger
import traceback
import boto3
import json


class AwsBoto3GetSecret(ManifestBase):
    """Retrieves a secret and stores the value in a variable for use by other manifests

The spec will allow custom Python code to be added for post-secret retrieval processing as may be required for dependent manifests that uses the secret value, for example when only a single value in a complex JSON object is required.

The following variable will be set once the secret is retrieved:

* `VALUE` - contains the secret value
* `TYPE` - Either "string" or "binary"

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
            self.spec['awsBoto3SessionReference'],
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
            return boto3_session.client('secretsmanager')
        raise Exception('Unable to create SecretsManager client')

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders())->bool:
        if target_environment not in self.metadata['environments']:
            return False
        return False

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='APPLY CALLED', level='info')

        value = None
        value_type = 'binary'
        client = self._get_boto3_s3_client(variable_cache=variable_cache, target_environment=target_environment)
        response = client.get_secret_value(SecretId=self.spec['secretName'])
        if 'SecretString' in response:
            value = response['SecretString']
            value_type = 'string'
        else:
            value = response['SecretBinary']

        if 'conversionTarget' in self.spec:
            if self.spec['conversionTarget'] == 'dict' and value_type == 'string':
                value = json.loads(value)
                value_type = 'dict'

        variable_cache.store_variable(
            variable=Variable(
                name='{}:VALUE'.format(self._var_name(target_environment=target_environment)),
                initial_value=value,
                logger=self.logger,
                mask_in_logs=True
            ),
            overwrite_existing=True
        )

        variable_cache.store_variable(
            variable=Variable(
                name='{}:TYPE'.format(self._var_name(target_environment=target_environment)),
                initial_value=value_type,
                logger=self.logger,
                mask_in_logs=False
            ),
            overwrite_existing=True
        )

        return 
    
    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='DELETE CALLED - reverting to APPLY to retrieve secret', level='info')
        self.apply_manifest(
            manifest_lookup_function=manifest_lookup_function,
            variable_cache=variable_cache,
            increment_exec_counter=increment_exec_counter,
            target_environment=target_environment,
            value_placeholders=value_placeholders
        )
        return 
