from py_animus.manifest_management import *
from py_animus import get_logger
import traceback
import boto3


class AwsBoto3Session(ManifestBase):
    """Provides a boto3 session object that can be used by other AWS manifests requiring AWS API access via Boto3.

The following variables will be set:

* `:CONNECTED` - A boolean value. If set to `True`, the session object can be used
* `:SESSION` - The Boto3 session object

> **Note**
> The IAM role used for the session must have the following minimum privileges required to set the `:CONNECTED` variable: `sts:GetCallerIdentity`

If the caller identity can be established, the session will be exposed for other services.

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
        
        connected_flag = variable_cache.get_value(
            variable_name='{}:CONNECTED'.format(self._var_name(target_environment=target_environment)),
            value_if_expired=False,
            default_value_if_not_found=False,
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        self.log(message='      connected_flag={}'.format(connected_flag), level='debug')
        if connected_flag is False:
            return True

        return False

    def _validate_supported_region(self, selected_region):
        if selected_region not in (
            'us-east-2',
            'us-east-1',
            'us-west-1',
            'us-west-2',
            'af-south-1',
            'ap-east-1',
            'ap-south-2',
            'ap-southeast-3',
            'ap-southeast-4',
            'ap-south-1',
            'ap-northeast-3',
            'ap-northeast-2',
            'ap-southeast-1',
            'ap-southeast-2',
            'ap-northeast-1',
            'ca-central-1',
            'eu-central-1',
            'eu-west-1',
            'eu-west-2',
            'eu-south-1',
            'eu-west-3',
            'eu-south-2',
            'eu-north-1',
            'eu-central-2',
            'me-south-1',
            'me-central-1',
            'sa-east-1',
        ):
            raise Exception('Invalid or unsupported AWS region.')
        
    def _profile_based_session(self, profile_name: str, aws_region: str):
        return boto3.session.Session(profile_name=profile_name, region_name=aws_region)

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='APPLY CALLED', level='info')
        if self.implemented_manifest_differ_from_this_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache, target_environment=target_environment, value_placeholders=value_placeholders) is False:
            self.log(message='   Script already executed', level='info')
            return
        
        aws_region = 'eu-central-1'
        if 'awsRegion' in self.spec:
            aws_region = self.spec['awsRegion'].lower()
        self._validate_supported_region(selected_region=aws_region)

        if 'profileName' in self.spec and 'awsAccessKeyId' in self.spec:
            raise Exception('Cannot have both "profileName" and "awsAccessKeyId" in spec.')
        
        if 'profileName' in self.spec:
            self.log(message='   Connecting to AWS in region "{}" using profile named "{}"'.format(aws_region, self.spec['profileName']), level='info')
            profile_name = self.spec['profileName']
            profile_name = profile_name.strip()
            variable_cache.store_variable(
                variable=Variable(
                    name='{}:SESSION'.format(self._var_name(target_environment=target_environment)),
                    initial_value=self._profile_based_session(profile_name=profile_name, aws_region=aws_region),
                    logger=self.logger
                ),
                overwrite_existing=True
            )
            variable_cache.store_variable(
                variable=Variable(
                    name='{}:CONNECTED'.format(self._var_name(target_environment=target_environment)),
                    initial_value=True,
                    logger=self.logger
                ),
                overwrite_existing=True
            )
        elif 'awsAccessKeyId' in self.spec:
            self.log(message='   Connecting to AWS in region "{}" using AWS Credentials'.format(aws_region), level='info')
        else:
            raise Exception('Either "profileName" or "awsAccessKeyId" must be defined in spec')
        
        return 
    
    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        """
            This is just a session and it may be used in the delete sequence in other manifests to delete remote resources and 
            therefore the set values need to remain or created if not yet created previously.
        """
        self.apply_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache, target_environment=target_environment, value_placeholders=value_placeholders)
        return 
