
from py_animus.manifest_management import *
from py_animus import get_logger, get_utc_timestamp




class AwsBoto3CloudFormationTemplate(ManifestBase):
    """Creates a new stack or applies a changeset in AWS CloudFormation.

When called with "apply" does one of two actions (default):

1. If the template has not been applied before, apply the new template
2. If the template was applied before, create and apply a change set

The behavior can be fine tuned with the `spec.changeDetection` settings

Variables to be set:

* `FINAL_STATUS` - string with the final CLoudFormation status
* `LOCAL_TEMPLATE_CHECKSUM` - string with the SHA256 checksum of the template in the local file (processed template - not the file checksum)
* `REMOTE_TEMPLATE_CHECKSUM` - string with the SHA256 checksum of the remote template (processed template - not the raw string checksum)
* And any additional mappings as defined in `spec.variableMappings`

The following CloudFormation status codes is assumed to indicate that the stack deployment is complete:

* `CREATE_COMPLETE`
* `CREATE_FAILED`
* `DELETE_COMPLETE`
* `DELETE_FAILED`
* `ROLLBACK_COMPLETE`
* `ROLLBACK_FAILED`
* `UPDATE_COMPLETE`
* `UPDATE_FAILED`
* `UPDATE_ROLLBACK_COMPLETE`
* `UPDATE_ROLLBACK_FAILED`
* `IMPORT_ROLLBACK_FAILED`
* `IMPORT_ROLLBACK_COMPLETE`

References:

* https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html
* https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-describing-stacks.html

    """

    def __init__(self, logger=get_logger(), post_parsing_method: object=None, version: str='v1', supported_versions: tuple=(['v1'])):
        super().__init__(logger=logger, post_parsing_method=post_parsing_method, version=version, supported_versions=supported_versions)

    def _var_name(self, target_environment: str='default'):
        return '{}:{}:{}'.format(
            self.__class__.__name__,
            self.metadata['name'],
            target_environment
        )

    def _get_boto3_cloudformation_client(self, variable_cache: VariableCache=VariableCache(), target_environment: str='default'):
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
            return boto3_session.client('cloudformation')
        raise Exception('Unable to create CloudFormation client')

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders())->bool:
        if target_environment not in self.metadata['environments']:
            return False

        cloudformation_client = self._get_boto3_cloudformation_client(variable_cache=variable_cache, target_environment=target_environment)

        return False

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='APPLY CALLED', level='info')

        cloudformation_client = self._get_boto3_cloudformation_client(variable_cache=variable_cache, target_environment=target_environment)

        return

    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='DELETE CALLED', level='info')

        cloudformation_client = self._get_boto3_cloudformation_client(variable_cache=variable_cache, target_environment=target_environment)

        return
