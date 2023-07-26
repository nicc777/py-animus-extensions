from py_animus.manifest_management import *
from py_animus import get_logger, get_utc_timestamp, parse_raw_yaml_data, logging
from py_animus import get_logger, get_utc_timestamp, logging
import re
import boto3
import hashlib
import json
import time


FINAL_STATES = (
    'CREATE_FAILED',
    'CREATE_COMPLETE',
    'ROLLBACK_FAILED',
    'ROLLBACK_COMPLETE',
    'DELETE_FAILED',
    'DELETE_COMPLETE',
    'UPDATE_COMPLETE',
    'UPDATE_FAILED',
    'UPDATE_ROLLBACK_FAILED',
    'UPDATE_ROLLBACK_COMPLETE',
    'NOT_FOUND',
)
ERROR_STATES = (
    'CREATE_FAILED',
    'ROLLBACK_FAILED',
    'ROLLBACK_COMPLETE',
    'DELETE_FAILED',
    'UPDATE_FAILED',
    'UPDATE_ROLLBACK_FAILED',
    'UPDATE_ROLLBACK_COMPLETE',
    'UNKNOWN',
)


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
        logging.getLogger('boto3').setLevel(logging.CRITICAL)
        logging.getLogger('botocore').setLevel(logging.CRITICAL)

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

        self.log(message='_set_variables(): INPUT ARG "target_environment"       : {}'.format(target_environment), level='debug')
        self.log(message='_set_variables(): INPUT ARG "status"                   : {}'.format(status), level='debug')
        self.log(message='_set_variables(): INPUT ARG "is_status_final"          : {}'.format(is_status_final), level='debug')
        self.log(message='_set_variables(): INPUT ARG "local_template_checksum"  : {}'.format(local_template_checksum), level='debug')
        self.log(message='_set_variables(): INPUT ARG "remote_template_checksum" : {}'.format(remote_template_checksum), level='debug')
        self.log(message='_set_variables(): INPUT ARG "outputs"                  : {}'.format(json.dumps(outputs, default=str)), level='debug')
        self.log(message='_set_variables(): INPUT ARG "resources"                : {}'.format(json.dumps(resources, default=str)), level='debug')

        variable_cache.store_variable(
            variable=Variable(
                name='{}:STACK_NAME'.format(self._var_name(target_environment=target_environment)),
                initial_value=self._format_template_name_as_stack_name(),
                logger=self.logger,
                mask_in_logs=False
            ),
            overwrite_existing=True
        )
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
        for output_variable_name, output_value in outputs.items():
            variable_cache.store_variable(
                variable=Variable(
                    name='{}:{}'.format(self._var_name(target_environment=target_environment), output_variable_name),
                    initial_value='{}'.format(output_value),
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

        for resource_key, resource_val in resources.items():
            variable_cache.store_variable(
                variable=Variable(
                    name='{}:{}'.format(self._var_name(target_environment=target_environment), resource_key),
                    initial_value=resource_val,
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
        self.log(message='_calculate_dict_checksum(): INPUT ARGS data                 : {}'.format(json.dumps(data, default=str)), level='debug')
        result = hashlib.sha256(json.dumps(data, default=str, sort_keys=True, ensure_ascii=True).encode('utf-8')).hexdigest()
        self.log(message='_calculate_dict_checksum(): RETURN result                   : {}'.format(json.dumps(result, default=str)), level='debug')
        return result

    def _calculate_local_template_checksum(self, parameters: list=list(), tags: list=list())->str:

        self.log(message='_calculate_local_template_checksum(): INPUT ARGS parameters : {}'.format(json.dumps(parameters, default=str)), level='debug')
        self.log(message='_calculate_local_template_checksum(): INPUT ARGS tags       : {}'.format(json.dumps(tags, default=str)), level='debug')

        file_content_as_str = None
        with open(self.spec['localTemplatePath'], 'r') as f:
            file_content_as_str = f.read()
        file_content_as_dict = self._attempt_to_convert_template_data_to_dict(data_as_str=file_content_as_str)
        file_content_as_dict['_PARAMETERS'] = list()
        file_content_as_dict['_TAGS'] = list()
        file_content_as_dict['_ADAPTED'] = True
        if len(parameters) > 0:
            file_content_as_dict['_PARAMETERS'] = parameters
        if len(tags) > 0:
            file_content_as_dict['_TAGS'] = tags

        result = self._calculate_dict_checksum(data=file_content_as_dict)
        self.log(message='_calculate_local_template_checksum(): RETURN result         : {}'.format(json.dumps(result, default=str)), level='debug')

        return result

    def _calculate_remote_template_checksum(self, stack_data: dict, stack_body_as_dict: dict)->str:

        self.log(message='_calculate_remote_template_checksum(): INPUT ARGS stack_data         : {}'.format(json.dumps(stack_data, default=str)), level='debug')
        self.log(message='_calculate_remote_template_checksum(): INPUT ARGS stack_body_as_dict : {}'.format(json.dumps(stack_body_as_dict, default=str)), level='debug')

        stack_body_as_dict['_PARAMETERS'] = list()
        stack_body_as_dict['_TAGS'] = list()
        stack_body_as_dict['_ADAPTED'] = True

        if 'Parameters' in stack_data:
            if stack_data['Parameters'] is not None:
                if isinstance(stack_data['Parameters'], list):
                    if len(stack_data['Parameters']) > 0:
                        stack_body_as_dict['_PARAMETERS'] = stack_data['Parameters']

        if 'Tags' in stack_data:
            if stack_data['Tags'] is not None:
                if isinstance(stack_data['Tags'], list):
                    if len(stack_data['Tags']) > 0:
                        stack_body_as_dict['_TAGS'] = stack_data['Tags']

        checksum = self._calculate_dict_checksum(data=stack_body_as_dict)

        self.log(message='_calculate_remote_template_checksum(): PROCESSED stack_body_as_dict  : {}'.format(json.dumps(stack_body_as_dict, default=str)), level='debug')
        self.log(message='_calculate_remote_template_checksum(): PROCESSED checksum            : {}'.format(checksum), level='debug')

        return checksum

    def _stack_exists(self, client, stack_name: str)->bool:
        remote_stack = self._get_current_remote_stack_data(cloudformation_client=client)
        if len(remote_stack) > 0:
            return True
        return False

    def _delete_stack(self, cloudformation_client, variable_cache: VariableCache=VariableCache(), target_environment: str='default'):
        stack_data = self._get_current_remote_stack_data(cloudformation_client=cloudformation_client)
        retry = True
        loop_counter = 0
        while retry is True:
            loop_counter += 1
            if stack_data['StackStatus'] in FINAL_STATES:
                retry = False
                cloudformation_client.delete_stack(StackName=stack_data['StackName'])
            else:
                self.log(message='CloudFormation stack "{}" is not yet in a final state to be deleted. Waiting...'.format(stack_data['StackName']), level='info')
                if loop_counter > 60:
                    raise Exception('CloudFormation stack "{}" did not get into a final state within an hour - aborting.'.format(stack_data['StackName']))
                time.sleep(30)
        time.sleep(10)
        final_state = self._track_progress_until_end_state(stack_id=stack_data['StackId'], variable_cache=variable_cache, target_environment=target_environment)
        self.log(message='Stack ID "{}" deleted with final status "{}"'.format(stack_data['StackId'], final_state), level='info')

    def _get_remote_stack_applied_template_as_dict(
        self,
        cloudformation_client,
        stack_name: str
    )->dict:
        template_data = dict()
        try:
            response = cloudformation_client.get_template(StackName=stack_name,TemplateStage='Original')
            if 'TemplateBody' in response:
                self.log(message='TemplateBody: {}'.format(response['TemplateBody']), level='debug')
                if isinstance(response['TemplateBody'], dict):
                    template_data = copy.deepcopy(response['TemplateBody'])
                elif isinstance(response['TemplateBody'], str):
                    template_data = self._attempt_to_convert_template_data_to_dict(data_as_str=response['TemplateBody'])
                else:
                    self.log(message='Returned data is in an invalid format. Received: {}'.format(response['TemplateBody']), level='error')
        except:
            self.log(message='It appears that the remote stack named "{}" does not exists'.format(stack_name), level='error')
        return template_data

    def _get_current_remote_stack_resource_data(
        self,
        cloudformation_client,
        stack_name: str
    )->list:
        resource_data = list()
        try:
            response = cloudformation_client.describe_stack_resources(StackName=stack_name)
            if 'StackResources' in response:
                for raw_resource_data in response['StackResources']:
                    if raw_resource_data['StackName'] == stack_name:
                        extracted_data = dict()
                        extracted_data['LogicalResourceId'] = 'Unknown'
                        extracted_data['PhysicalResourceId'] = 'Unknown'
                        extracted_data['ResourceType'] = 'Unknown'
                        extracted_data['ResourceStatus'] = 'Unknown'
                        if 'LogicalResourceId' in raw_resource_data:
                            extracted_data['LogicalResourceId'] = raw_resource_data['LogicalResourceId']
                        if 'PhysicalResourceId' in raw_resource_data:
                            extracted_data['PhysicalResourceId'] = raw_resource_data['PhysicalResourceId']
                        if 'ResourceType' in raw_resource_data:
                            extracted_data['ResourceType'] = raw_resource_data['ResourceType']
                        if 'ResourceStatus' in raw_resource_data:
                            extracted_data['ResourceStatus'] = raw_resource_data['ResourceStatus']
                        resource_data.append(extracted_data)
        except:
            self.log(message='It appears that the remote stack named "{}" does not exists'.format(stack_name), level='error')
        return resource_data

    def _get_current_remote_stack_data(
        self,
        cloudformation_client
    )->dict:
        remote_stack_data = dict()  # Refer to https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/describe_stacks.html
        try:
            response = cloudformation_client.describe_stacks(
                StackName=self._format_template_name_as_stack_name()
            )
            if 'Stacks' in response:
                for stack_data in response['Stacks']:
                    if stack_data['StackName'] == self._format_template_name_as_stack_name():
                        remote_stack_data = copy.deepcopy(stack_data)
                        remote_stack_data['StackResources'] = self._get_current_remote_stack_resource_data(
                            cloudformation_client=cloudformation_client,
                            stack_name=self._format_template_name_as_stack_name()
                        )
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
        next_action = variable_cache.get_value(
            variable_name='{}:NEXT_ACTION'.format(self._var_name(target_environment=target_environment)),
            value_if_expired='PENDING',
            default_value_if_not_found='NOT_YET_CHECKED',
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )

        self.log(message='implemented_manifest_differ_from_this_manifest(): current_parsed_parameters : {}'.format(json.dumps(current_parsed_parameters, default=str)), level='debug')
        self.log(message='implemented_manifest_differ_from_this_manifest(): current_parsed_tags       : {}'.format(json.dumps(current_parsed_tags, default=str)), level='debug')
        self.log(message='implemented_manifest_differ_from_this_manifest(): current_processing_status : {}'.format(current_processing_status), level='debug')

        action_compare_checksums_and_parameters = False

        remote_stack_data = dict()
        remote_stack_template_body_as_dict = dict()

        try:
            remote_stack_data = self._get_current_remote_stack_data(cloudformation_client)
        except:
            self.log(message='implemented_manifest_differ_from_this_manifest(): Failed to retrieve remote stack data', level='warning')
        if len(remote_stack_data) > 0:
            action_compare_checksums_and_parameters = True
            self.log(message='implemented_manifest_differ_from_this_manifest(): Stack was deployed previously. Next step is to compare checksums of the templates and parameters to see if a changeset is required.', level='info')
            remote_stack_template_body_as_dict = self._get_remote_stack_applied_template_as_dict(cloudformation_client=cloudformation_client, stack_name=self._format_template_name_as_stack_name())
        else:
            variable_cache.store_variable(
                variable=Variable(
                    name='{}:NEXT_ACTION'.format(self._var_name(target_environment=target_environment)),
                    initial_value='DEPLOY_NEW_STACK',
                    logger=self.logger
                ),
                overwrite_existing=True
            )
            self.log(message='implemented_manifest_differ_from_this_manifest(): First/New deployment - A new stack will be created', level='info')
            return True

        if action_compare_checksums_and_parameters is True:
            local_template_checksum = self._calculate_local_template_checksum(parameters=current_parsed_parameters, tags=current_parsed_tags)
            remote_template_checksum = self._calculate_remote_template_checksum(stack_data=remote_stack_data, stack_body_as_dict=remote_stack_template_body_as_dict)
            self.log(message='implemented_manifest_differ_from_this_manifest(): Comparing local_template_checksum with value "{}" to remote_template_checksum with value of "{}"'.format(local_template_checksum, remote_template_checksum), level='info')
            if local_template_checksum != remote_template_checksum:
                variable_cache.store_variable(
                    variable=Variable(
                        name='{}:NEXT_ACTION'.format(self._var_name(target_environment=target_environment)),
                        initial_value='DEPLOY_CHANGE_SET',
                        logger=self.logger
                    ),
                    overwrite_existing=True
                )
                self.log(message='implemented_manifest_differ_from_this_manifest(): A ChangeSet needs to be applied', level='info')
                return True
            else:
                self.log(message='implemented_manifest_differ_from_this_manifest(): The current deployment does NOT have to be updated', level='info')

        return False

    def _set_stack_options(self)->dict:
        stack_options = {
            'DisableRollback': False,
            'TimeoutInMinutes': 10,
            'NotificationARNs': list(),
            'Capabilities': list(),
            'OnFailure': 'ROLLBACK',
            'EnableTerminationProtection': False,
        }
        use_disable_rollback = False
        if 'options' in self.spec:

            if 'onFailure' not in self.spec['options']:
                use_disable_rollback = True
                stack_options.pop('OnFailure')
            else:
                stack_options.pop('DisableRollback')

            if 'disableRollback' in self.spec['options'] and use_disable_rollback is True:
                if isinstance(self.spec['options']['disableRollback'], bool):
                    stack_options['DisableRollback'] = self.spec['options']['disableRollback']
            elif 'disableRollback' in self.spec['options'] and use_disable_rollback is False:
                self.log(message='Cannot use "disableRollback" together with "onFailure" - it is either the one or the other. The "onFailure" option gets priority.', level='warning')
            if 'timeoutInMinutes' in self.spec['options']:
                if isinstance(self.spec['options']['timeoutInMinutes'], int):
                    if self.spec['options']['timeoutInMinutes'] < 10:
                        self.log(message='timeoutInMinutes less than minimum of value 10 - using value 10', level='warning')
                        stack_options['TimeoutInMinutes'] = 10
                    elif self.spec['options']['timeoutInMinutes'] > 60:
                        self.log(message='timeoutInMinutes greater than maximum of value 60 - using value 60', level='warning')
                        stack_options['TimeoutInMinutes'] = 60
                    else:
                        stack_options['TimeoutInMinutes'] = self.spec['options']['timeoutInMinutes']
            if 'notificationARNs' in self.spec['options']:
                if isinstance(self.spec['options']['notificationARNs'], list):
                    arns = list()
                    for arn in self.spec['options']['notificationARNs']:
                        if arn is not None:
                            if isinstance(arn, str):
                                if arn.startswith('arn:'):
                                    arns.append(arn)
                    stack_options['NotificationARNs'] = arns
            else:
                stack_options.pop('NotificationARNs')
            if 'capabilities' in self.spec['options']:
                if isinstance(self.spec['options']['capabilities'], bool):
                    capabilities = list()
                    for capability in self.spec['options']['capabilities']:
                        if capability is not None:
                            if isinstance(capability, str):
                                if self.spec['options']['capabilities'] in ('CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND', ):
                                    capabilities.append(capability)
                    stack_options['Capabilities'] = capabilities
            else:
                stack_options.pop('Capabilities')
            if 'onFailure' in self.spec['options'] and use_disable_rollback is False:
                if self.spec['options']['onFailure'] is not None:
                    if isinstance(self.spec['options']['onFailure'], str):
                        if self.spec['options']['onFailure'] in ('DO_NOTHING', 'ROLLBACK', 'DELETE'):
                            stack_options['OnFailure'] = self.spec['options']['onFailure']
            if 'enableTerminationProtection' in self.spec['options']:
                if isinstance(self.spec['options']['enableTerminationProtection'], bool):
                    stack_options['EnableTerminationProtection'] = self.spec['options']['enableTerminationProtection']
        else:
            stack_options.pop('DisableRollback')
            stack_options.pop('NotificationARNs')
            stack_options.pop('Capabilities')
        self.log(message='Initial stack_options: {}'.format(json.dumps(stack_options)), level='info')
        return stack_options

    def _track_progress_until_end_state(self, stack_id: str, variable_cache: VariableCache=VariableCache(), target_environment: str='default')->str:
        end_state_reached = False
        cloudformation_client = self._get_boto3_cloudformation_client(variable_cache=variable_cache, target_environment=target_environment)
        final_state = 'UNKNOWN'
        self.log(message='Waiting for stack "{}" to finish'.format(stack_id), level='info')
        loop_count = 0
        while end_state_reached is False:
            loop_count += 1
            self.log(message='    Sleeping 30 seconds', level='info')
            time.sleep(30)
            stack_data = self._get_current_remote_stack_data(cloudformation_client)
            self.log(message='stack_data: {}'.format(json.dumps(stack_data, default=str)), level='debug')
            try:
                if stack_data['StackId'] == stack_id:
                    self.log(message='        Stack ID "{}" progress status: {}'.format(stack_id, stack_data['StackStatus']), level='info')
                    if stack_data['StackStatus'] in FINAL_STATES:
                        end_state_reached = True
                        final_state = stack_data['StackStatus']
            except:
                self.log(message='Stack data could not be retrieved - likely because stack does not exist (yet). Setting final_state to "NOT_FOUND"', level='info')
                final_state = 'NOT_FOUND'
                end_state_reached = True
            if loop_count > 120:
                self.log(message='Waited for more than 2 hours - giving up', level='warning')
                end_state_reached = True
        raise_Exception_on_final_states_tuple = (
            'CREATE_FAILED',
            'ROLLBACK_FAILED',
            'DELETE_FAILED',
            'UPDATE_FAILED',
            'UPDATE_ROLLBACK_FAILED',
            'IMPORT_ROLLBACK_FAILED',
            'UNKNOWN',
        )
        if final_state in ERROR_STATES:
            if 'raiseExceptionOnFinalStatusValues' not in self.spec:
                self.spec['raiseExceptionOnFinalStatusValues'] = list(raise_Exception_on_final_states_tuple)
            if isinstance(self.spec['raiseExceptionOnFinalStatusValues'], list):
                for state in self.spec['raiseExceptionOnFinalStatusValues']:
                    if state is not None:
                        if isinstance(state, str):
                            if state.upper() == final_state:
                                raise Exception('Cannot proceed due to final state being "{}"'.format(final_state))
        return final_state

    def _extract_outputs_from_stack_data(self, stack_data: dict=dict())->dict:
        outputs = dict()
        variable_mappings = dict()
        if 'variableMappings' in self.spec:
            if 'outputs' in self.spec['variableMappings']:
                for mapping_item in self.spec['variableMappings']['outputs']:
                    variable_mappings[mapping_item['outputKey']] = mapping_item['variableName'] # { 'MyCredentialsArn': 'SECRET_ARN' }
        self.log(message='_extract_outputs_from_stack_data(): variable_mappings: {}'.format(json.dumps(variable_mappings)), level='debug')

        if 'Outputs' in stack_data:
            for output_data_item in stack_data['Outputs']:
                if 'OutputKey' in output_data_item and 'OutputValue' in output_data_item:
                    key = output_data_item['OutputKey']     # MyCredentialsArn
                    value = output_data_item['OutputValue']   # arn:aws:.......
                    self.log(message='_extract_outputs_from_stack_data(): key="{}"   value="{}"'.format(key, value), level='debug')
                    if key in variable_mappings:
                        self.log(message='  key="{}" FOUND in variable_mappings'.format(key, value), level='debug')
                        variable_name = variable_mappings[key]
                        self.log(message='  variable_name="{}"'.format(variable_name), level='debug')
                        outputs[variable_name] = value
                    else:
                        self.log(message='  key="{}" NOT FOUND in variable_mappings'.format(key, value), level='debug')
        self.log(message='_extract_outputs_from_stack_data(): PRE-RETURN: outputs: {}'.format(json.dumps(outputs)), level='debug')  # {"SECRET_ARN": "arn:aws:......."}
        return outputs

    def _extract_resources_from_stack_data(self, stack_data: dict=dict())->dict:
        self.log(message='_extract_resources_from_stack_data(): stack_data: {}'.format(json.dumps(stack_data, default=str)), level='debug')
        resources = dict()
        variable_mappings = dict()
        if 'variableMappings' in self.spec:
            if 'resources' in self.spec['variableMappings']:
                for mapping_item in self.spec['variableMappings']['resources']:
                    variable_mappings[mapping_item['logicalResourceId']] = dict()
                    for resource_variable_mapping_data in mapping_item['variables']:
                        for resource_field_name, target_variable_name in resource_variable_mapping_data.items():
                            final_resource_field_name = resource_field_name[0].upper() + resource_field_name[1:]
                            variable_mappings[mapping_item['logicalResourceId']][final_resource_field_name] = target_variable_name
        self.log(message='_extract_resources_from_stack_data(): variable_mappings: {}'.format(json.dumps(variable_mappings, default=str)), level='debug')
        if 'StackResources' in stack_data:
            for resource_data_item in stack_data['StackResources']:
                if 'LogicalResourceId' in resource_data_item:
                    self.log(message='_extract_resources_from_stack_data(): resource_data_item["LogicalResourceId"]: {}'.format(resource_data_item['LogicalResourceId']), level='debug')
                    if resource_data_item['LogicalResourceId'] in variable_mappings:
                        mapping_data = variable_mappings[resource_data_item['LogicalResourceId']]

                        self.log(message='_extract_resources_from_stack_data(): mapping_data: {}'.format(json.dumps(mapping_data, default=str)), level='debug')

                        for mapping_key, target_variable_name in mapping_data.items():
                            if mapping_key in resource_data_item:
                                resources[target_variable_name] = resource_data_item[mapping_key]
        self.log(message='_extract_resources_from_stack_data(): PRE-RETURN: resources: {}'.format(json.dumps(resources, default=str)), level='debug')  # {"CREDS_RESOURCE_TYPE": "AWS::SecretsManager::Secret", ...}
        return resources

    def _apply_cloudformation_stack(self, variable_cache: VariableCache=VariableCache(), target_environment: str='default'):
        parameters = self._set_stack_options()
        self.log(message='parameters={}'.format(json.dumps(parameters)), level='debug')

        if 'templatePath' in self.spec:
            if self.spec['templatePath'].lower().startswith('https://s3.amazonaws.com/'):
                parameters['TemplateURL'] = '{}'.format(self.spec['templatePath'])
            else:
                content = ''
                with open(self.spec['templatePath'], 'r') as f:
                    content = f.read()
                if len(content) > 0:
                    parameters['TemplateBody'] = content
                else:
                    raise Exception('Could not load content')
        else:
            raise Exception('Expected field "templatePath" in spec.')

        parameters_as_list = variable_cache.get_value(
            variable_name='{}:PARSED_PARAMETERS_AS_LIST'.format(self._var_name(target_environment=target_environment)),
            value_if_expired=list(),
            default_value_if_not_found=list(),
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        tags_as_list = variable_cache.get_value(
            variable_name='{}:PARSED_TAGS_AS_LIST'.format(self._var_name(target_environment=target_environment)),
            value_if_expired=list(),
            default_value_if_not_found=list(),
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        if len(parameters_as_list) > 0:
            parameters['Parameters'] = parameters_as_list
        if len(tags_as_list) > 0:
            parameters['Tags'] = tags_as_list
        parameters['StackName'] = self._format_template_name_as_stack_name()

        response = dict()
        self.log(message='Final Parameters for Boto3 CloudFormation Stack: {}'.format(json.dumps(parameters)), level='debug')
        cloudformation_client = self._get_boto3_cloudformation_client(variable_cache=variable_cache, target_environment=target_environment)
        response = cloudformation_client.create_stack(**parameters)
        self.log(message='New cloudwatch Stack AWS API Response: {}'.format(json.dumps(response)), level='info')

        if 'StackId' in response:
            time.sleep(10)
            final_state = self._track_progress_until_end_state(stack_id=response['StackId'], variable_cache=variable_cache, target_environment=target_environment)
            stack_data = self._get_current_remote_stack_data(cloudformation_client)
            remote_stack_template_body_as_dict = self._get_remote_stack_applied_template_as_dict(cloudformation_client=cloudformation_client, stack_name=parameters['StackName'])
            self._set_variables(
                variable_cache=variable_cache,
                target_environment=target_environment,
                status=final_state,
                is_status_final=True,
                local_template_checksum=self._calculate_local_template_checksum(parameters=parameters_as_list, tags=tags_as_list),
                remote_template_checksum=self._calculate_remote_template_checksum(stack_data=stack_data, stack_body_as_dict=remote_stack_template_body_as_dict),
                outputs=self._extract_outputs_from_stack_data(stack_data=stack_data),
                resources=self._extract_resources_from_stack_data(stack_data=stack_data)
            )
        self.log(message='Stack ID "{}" applied with final status "{}"'.format(response['StackId'], final_state), level='info')

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='APPLY CALLED', level='info')

        if self.implemented_manifest_differ_from_this_manifest(
            manifest_lookup_function=manifest_lookup_function,
            variable_cache=variable_cache,
            target_environment=target_environment,
            value_placeholders=value_placeholders
        ) is False:
            self.log(message='apply_manifest(): Stack already deployed and no new changes detected.', level='info')
            return

        change_type = variable_cache.get_value(
            variable_name='{}:NEXT_ACTION'.format(self._var_name(target_environment=target_environment)),
            value_if_expired='NONE',
            default_value_if_not_found='NONE',
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        self.log(message='apply_manifest(): Apply Action: {}'.format(change_type), level='info')
        if change_type in ('NONE', 'NOTHING'):
            self.log(message='apply_manifest(): Final Action: NONE / NOTHING', level='info')
            return

        if change_type == 'DEPLOY_NEW_STACK':
            self.log(message='apply_manifest(): Final Action: DEPLOY_NEW_STACK', level='info')
            self._apply_cloudformation_stack(variable_cache=variable_cache, target_environment=target_environment)

        if change_type == 'DEPLOY_CHANGE_SET':
            # TODO deploy change set
            self.log(message='apply_manifest(): Final Action: DEPLOY_CHANGE_SET', level='info')
            pass

        return

    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='DELETE CALLED', level='info')

        cloudformation_client = self._get_boto3_cloudformation_client(variable_cache=variable_cache, target_environment=target_environment)
        stack_name = self._format_template_name_as_stack_name()

        if self._stack_exists(client=cloudformation_client, stack_name=stack_name) is True:
            self._delete_stack(cloudformation_client=cloudformation_client, variable_cache=variable_cache, target_environment=target_environment)

        return
