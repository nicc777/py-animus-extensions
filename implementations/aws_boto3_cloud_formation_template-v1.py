
from py_animus.manifest_management import *
from py_animus import get_logger, get_utc_timestamp, parse_raw_yaml_data
import re
import boto3
import hashlib
import json

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

    def _attempt_to_convert_template_data_to_dict(self, data_as_str: str)->dict:
        parse_exception = False
        stack_template_data_as_dict =dict()
        try:
            stack_template_data_as_dict = json.loads(data_as_str)
        except:
            self.log(message='Failed to convert JSON to DICT - attempting YAML to DICT conversion.', level='warning')
            try:
                stack_template_data_as_dict = parse_raw_yaml_data(yaml_data=data_as_str, logger=self.logger)['part_1']
            except:
                self.log(message='All attempts to parse the remote template failed!', level='error')
                parse_exception = True
        if parse_exception is True:
            raise Exception('Failed to parse the remote CloudFormation Template data')
        return stack_template_data_as_dict

    def _calculate_dict_checksum(self, data: dict=dict())->str:
        return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=True).encode('utf-8')).hexdigest()

    def _calculate_local_template_checksum(self)->str:
        file_content_as_str = None
        with open(self.spec['templatePath'], 'r') as f:
            file_content_as_str = f.read()
        return self._calculate_dict_checksum(data=self._attempt_to_convert_template_data_to_dict(data_as_str=file_content_as_str))

    def _stack_exists(self, client, stack_name: str)->bool:
        remote_stack = self._get_current_remote_stack_status(cloudformation_client=client)
        if len(remote_stack) > 0:
            return True
        return False

    def _delete_stack(self, client, stack_name: str):
        # TODO complete implementation...
        pass

    def _get_current_remote_stack_status(
            self,
            cloudformation_client
        )->dict:
        remote_stack_data = dict()  # Refer to https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/describe_stacks.html
        try:
            response = cloudformation_client.describe_stacks(
                StackName=self._format_template_name_as_stack_name()
            )
            if 'Stacks' in response:
                remote_stack_data = response['Stacks'][0]
        except:
            self.log(message='It appears that the remote stack named "{}" does not exists'.format(self._format_template_name_as_stack_name()), level='error')
        return remote_stack_data

    def _get_current_remote_stack_template(
            self,
            cloudformation_client
        )->dict:
        remote_stack_template = dict()  # Convert the template to DICT
        response = cloudformation_client.get_template(
            StackName=self._format_template_name_as_stack_name(),
            TemplateStage='Original'
        )
        if 'TemplateBody' in response:
            remote_stack_template = self._attempt_to_convert_template_data_to_dict(data_as_str=response['TemplateBody'])
        return remote_stack_template

    def _format_template_name_as_stack_name(self)->str:
        tmp_name = re.sub('[^0-9a-zA-Z]+', '_', self.metadata['name'])
        name = ''
        for word in tmp_name.split('_'):
            if len(word) > 0:
                name = '{}{}'.format(name, word.capitalize())
        return name

    def _is_local_template_and_parameters_different_from_remote_template_and_parameters(self, remote_template_meta_data: dict, remote_template_as_dict: dict)->bool:
        # TODO complete implemention
        return False

    def _get_parameters(self, variable_cache: VariableCache=VariableCache(), target_environment: str='default')->list:
        parameters = list()
        if 'parameterReferences' in self.spec:
            for parameter_reference in self.spec['parameterReferences']:
                self.log(message='Processing parameter reference "{}"'.format(parameter_reference), level='info')
                if ':' not in parameter_reference:
                    parameter_variable_name = 'AwsBoto3CloudFormationTemplateParameters:{}:{}'.format(
                        parameter_reference,
                        target_environment
                    )
                else:
                    parameter_variable_name = parameter_reference
                self.log(message='   Looking up parameters variable named "{}"'.format(parameter_variable_name), level='debug')
                for parameter_key, parameter_value in variable_cache.get_value( # Expect format "{ "<<parameter_key>>": "<<parameter_value>>" }"
                    variable_name='{}:PARAMETERS'.format(parameter_variable_name),
                    value_if_expired=dict(),
                    default_value_if_not_found=dict(),
                    raise_exception_on_expired=False,
                    raise_exception_on_not_found=False
                ).items():                                                      # Convert into format {'ParameterKey': 'string', 'ParameterValue': 'string'}
                    final_value = '{}'.format(parameter_value)
                    if parameter_value is None:
                        final_value = parameter_value
                    elif isinstance(parameter_value, bool):
                        final_value = parameter_value
                    parameters.append(
                        {
                            'ParameterKey': parameter_key,
                            'ParameterValue': final_value,
                        }
                    )
        self.log(message='parameters: {}'.format(json.dumps(parameters)), level='debug')
        return parameters

    def _get_tags(self, variable_cache: VariableCache=VariableCache(), target_environment: str='default')->list:
        tags = list()
        if 'tagReferences' in self.spec:
            for tag_reference in self.spec['tagReferences']:
                self.log(message='Processing tags reference "{}"'.format(tag_reference), level='info')
                if ':' not in tag_reference:
                    tag_variable_name = 'AwsBoto3CloudFormationTemplateTags:{}:{}'.format(
                        tag_reference,
                        target_environment
                    )
                else:
                    tag_variable_name = tag_reference
                self.log(message='   Looking up parameters variable named "{}"'.format(tag_variable_name), level='debug')
                for tag_key, tag_value in variable_cache.get_value(             # Expect format "{ "<<tag_key>>": "<<tag_value>>" }"
                    variable_name='{}:TAGS'.format(tag_variable_name),
                    value_if_expired=dict(),
                    default_value_if_not_found=dict(),
                    raise_exception_on_expired=False,
                    raise_exception_on_not_found=False
                ).items():                                                      # Convert into format {'Key': 'string', 'Value': 'string'}
                    final_value = '{}'.format(tag_value)
                    if tag_value is None:
                        final_value = tag_value
                    elif isinstance(tag_value, bool):
                        final_value = tag_value
                    tags.append(
                        {
                            'Key': tag_key,
                            'Value': final_value,
                        }
                    )
        self.log(message='parameters: {}'.format(json.dumps(tags)), level='debug')
        return tags

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders())->bool:
        if target_environment not in self.metadata['environments']:
            return False

        ###
        ### Process Parameters and Tags
        ###
        current_parsed_parameters = variable_cache.get_value(
            variable_name='{}:PARSED_PARAMETERS_AS_LIST'.format(self._var_name(target_environment=target_environment)),
            value_if_expired=self._get_parameters(variable_cache=variable_cache, target_environment=target_environment),
            default_value_if_not_found=self._get_parameters(variable_cache=variable_cache, target_environment=target_environment),
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        current_parsed_tags = variable_cache.get_value(
            variable_name='{}:PARSED_TAGS_AS_LIST'.format(self._var_name(target_environment=target_environment)),
            value_if_expired=self._get_tags(variable_cache=variable_cache, target_environment=target_environment),
            default_value_if_not_found=self._get_tags(variable_cache=variable_cache, target_environment=target_environment),
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:PARSED_PARAMETERS_AS_LIST'.format(self._var_name(target_environment=target_environment)),
                initial_value=current_parsed_parameters,
                logger=self.logger
            ),
            overwrite_existing=False
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:PARSED_TAGS_AS_LIST'.format(self._var_name(target_environment=target_environment)),
                initial_value=current_parsed_tags,
                logger=self.logger
            ),
            overwrite_existing=False
        )


        ###
        ### Check previous processing status to determine next actions
        ###
        cloudformation_client = self._get_boto3_cloudformation_client(variable_cache=variable_cache, target_environment=target_environment)
        current_processing_status = variable_cache.get_value(
            variable_name='{}:PROCESSING_STATUS'.format(self._var_name(target_environment=target_environment)),
            value_if_expired='NOT_STARTED',
            default_value_if_not_found='NOT_YET_CHECKED',
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        current_processing_status = variable_cache.get_value(
            variable_name='{}:NEXT_ACTION'.format(self._var_name(target_environment=target_environment)),
            value_if_expired='PENDING',
            default_value_if_not_found='NOT_YET_CHECKED',
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )

        action_get_remote_stack_data = False
        action_calculate_local_template_checksum = False
        action_compare_checksums_and_parameters = False

        remote_stack_data = dict()

        if current_processing_status == 'NOT_STARTED':
            action_get_remote_stack_data = True
            action_calculate_local_template_checksum = True
        elif current_processing_status == 'DONE':
            return False

        if action_get_remote_stack_data is True:
            remote_stack_data = self._get_current_remote_stack_status(cloudformation_client)
        if len(remote_stack_data) > 0:
            action_compare_checksums_and_parameters = True
            current_processing_status = variable_cache.get_value(
                variable_name='{}:NEXT_ACTION'.format(self._var_name(target_environment=target_environment)),
                value_if_expired='CHANGE_SET_DECISION_PENDING',
                default_value_if_not_found='NOT_YET_CHECKED',
                raise_exception_on_expired=False,
                raise_exception_on_not_found=False
            )
            self.log(message='Stack was deployed previously. Next step is to compare checksums of the templates and parameters to see if a changeset is required.', level='info')
        else:
            current_processing_status = variable_cache.get_value(
                variable_name='{}:NEXT_ACTION'.format(self._var_name(target_environment=target_environment)),
                value_if_expired='CREATE_NEW_STACK',
                default_value_if_not_found='NOT_YET_CHECKED',
                raise_exception_on_expired=False,
                raise_exception_on_not_found=False
            )
            self.log(message='First/New deployment - A new stack will be created', level='info')
            return True

        if action_calculate_local_template_checksum is True:
            pass

        if action_compare_checksums_and_parameters is True:
            pass

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
