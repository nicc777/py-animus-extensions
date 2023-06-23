
from py_animus.manifest_management import *
from py_animus import get_logger, get_utc_timestamp
import re
import boto3

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

    def _set_variables(
            self,
            variable_cache: VariableCache=VariableCache(),
            target_environment: str='default',
            status: str='UNKNOWN',
            is_status_final: bool=False,
            local_template_checksum: str=None,
            remote_template_checksum: str=None,
            outputs: dict=dict(),
            resources: dict=dict()
        ):
        if is_status_final is True:
            variable_cache.store_variable(
                variable=Variable(
                    name='{}:FINAL_STATUS'.format(self._var_name(target_environment=target_environment)),
                    initial_value=status,
                    logger=self.logger,
                    mask_in_logs=False
                ),
                overwrite_existing=True
            )
            variable_cache.store_variable(
                variable=Variable(
                    name='{}:PROCESSING_STATUS'.format(self._var_name(target_environment=target_environment)),
                    initial_value='DONE',
                    logger=self.logger,
                    mask_in_logs=False
                ),
                overwrite_existing=True
            )
        else:
            variable_cache.store_variable(
                variable=Variable(
                    name='{}:PROCESSING_STATUS'.format(self._var_name(target_environment=target_environment)),
                    initial_value=status,
                    logger=self.logger,
                    mask_in_logs=False
                ),
                overwrite_existing=True
            )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:LOCAL_TEMPLATE_CHECKSUM'.format(self._var_name(target_environment=target_environment)),
                initial_value=local_template_checksum,
                logger=self.logger,
                mask_in_logs=False
            ),
            overwrite_existing=True
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:REMOTE_TEMPLATE_CHECKSUM'.format(self._var_name(target_environment=target_environment)),
                initial_value=remote_template_checksum,
                logger=self.logger,
                mask_in_logs=False
            ),
            overwrite_existing=True
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:OUTPUTS'.format(self._var_name(target_environment=target_environment)),
                initial_value=outputs,
                logger=self.logger,
                mask_in_logs=False
            ),
            overwrite_existing=True
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:RESOURCES'.format(self._var_name(target_environment=target_environment)),
                initial_value=resources,
                logger=self.logger,
                mask_in_logs=False
            ),
            overwrite_existing=True
        )

    def _calculate_dict_checksum(self, data: dict=dict())->str:
        pass

    def _stack_exists(self, client, stack_name: str)->bool:
        return False

    def _delete_stack(self, client, stack_name: str):
        pass

    def _get_current_remote_stack_status(
            self,
            cloudformation_client,
            VariableCache=VariableCache(),
            target_environment: str='default'
        )->dict:
        pass

    def _format_template_name_as_stack_name(self)->str:
        tmp_name = re.sub('[^0-9a-zA-Z]+', '_', self.metadata['name'])
        name = ''
        for word in tmp_name.split('_'):
            if len(word) > 0:
                name = '{}{}'.format(name, word.capitalize())
        return name

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders())->bool:
        if target_environment not in self.metadata['environments']:
            return False

        cloudformation_client = self._get_boto3_cloudformation_client(variable_cache=variable_cache, target_environment=target_environment)
        current_processing_status = variable_cache.get_value(
            variable_name='{}:PROCESSING_STATUS'.format(self._var_name(target_environment=target_environment)),
            value_if_expired='NOT_STARTED',
            default_value_if_not_found='NOT_YET_CHECKED',
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )

        action_get_remote_stack_data = False
        action_calculate_local_template_checksum = False

        if current_processing_status == 'NOT_STARTED':
            action_get_remote_stack_data = True
            action_calculate_local_template_checksum = True
        elif current_processing_status == 'DONE':
            return False

        return False

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='APPLY CALLED', level='info')

        cloudformation_client = self._get_boto3_cloudformation_client(variable_cache=variable_cache, target_environment=target_environment)

        if self.implemented_manifest_differ_from_this_manifest(
            manifest_lookup_function=manifest_lookup_function,
            variable_cache=variable_cache,
            target_environment=target_environment,
            value_placeholders=value_placeholders
        ) is False:
            return

        return

    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='DELETE CALLED', level='info')

        cloudformation_client = self._get_boto3_cloudformation_client(variable_cache=variable_cache, target_environment=target_environment)
        stack_name = self._format_template_name_as_stack_name()

        if self._stack_exists(client=cloudformation_client, stack_name=stack_name) is True:
            self._delete_stack(client=cloudformation_client, stack_name=stack_name)

        return
