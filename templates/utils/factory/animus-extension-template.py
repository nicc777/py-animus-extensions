from py_animus.manifest_management import *
from py_animus import get_logger, parse_raw_yaml_data
from py_animus.utils import *
from py_animus.py_animus import run_main
import traceback
import os
from functools import reduce
import re
from typing import Any, Optional
import sys
from pathlib import Path
import shutil
import inspect
import json


DOC_BASE_PATH = '{}{}doc'.format(
    os.getcwd(),
    os.sep
)

EXAMPLES_BASE_PATH = '{}{}examples'.format(
    os.getcwd(),
    os.sep
)

IMPLEMENTATIONS_BASE_PATH = '{}{}implementations'.format(
    os.getcwd(),
    os.sep
)

DOC_TEMPLATE_SCENARIO_EXAMPLE = """## Example for `__SCENARIO__` scenarios

```shell
export SCENARIO_NAME="__SCENARIO__"
```

Example manifest:

```yaml
__MINIMAL_TEMPLATE__
```

__SCENARIO_DESCRIPTION__
"""


# From: https://stackoverflow.com/questions/12414821/checking-a-nested-dictionary-using-a-dot-notation-string-a-b-c-d-e-automatica
def find_key(dot_notation_path: str, payload: dict) -> Any:
    def get_despite_none(payload: Optional[dict], key: str) -> Any:
        if not payload or not isinstance(payload, (dict, list)):
            return None
        if (num_key := re.match(r"^\[(\d+)\]$", key)) is not None:
            try:
                return payload[int(num_key.group(1))]
            except IndexError:
                return None
        else:
            return payload.get(key, None)
    found = reduce(get_despite_none, dot_notation_path.split("."), payload)
    return found


class AnimusExtensionTemplate(ManifestBase):

    def __init__(self, logger=get_logger(), post_parsing_method: object=None, version: str='v1', supported_versions: tuple=('v1',)):
        super().__init__(logger=logger, post_parsing_method=post_parsing_method, version=version, supported_versions=supported_versions)

    def _var_name(self):
        return '{}:{}'.format(
            self.__class__.__name__,
            self.metadata['name']
        )

    def _validate_str_or_list_or_boolean(
            self,
            spec_path: str,
            value: str,
            value_type: type,
            default_val: str='',
            set_default_when_not_present: bool=True,        # If false and field is not present, raise exception
            set_default_when_type_mismatch: bool=False,     # By default and exception will be raised
            set_default_when_null: bool=True,               # If false and value is None, raise an exception
            raise_exception_when_empty: bool=False,
            log_indent_spaces: int=0
        )->object:
        # self.log(message='        + spec_path                      = {}'.format( spec_path                      ), level='debug')
        # self.log(message='        + value                          = {}'.format( value                          ), level='debug')
        # self.log(message='        + value_type                     = {}'.format( value_type                     ), level='debug')
        # self.log(message='        + default_val                    = {}'.format( default_val                    ), level='debug')
        # self.log(message='        + set_default_when_not_present   = {}'.format( set_default_when_not_present   ), level='debug')
        # self.log(message='        + set_default_when_type_mismatch = {}'.format( set_default_when_type_mismatch ), level='debug')
        # self.log(message='        + set_default_when_null          = {}'.format( set_default_when_null          ), level='debug')
        # self.log(message='        + raise_exception_when_empty     = {}'.format( raise_exception_when_empty     ), level='debug')
        final_value = default_val
        if value is not None:
            final_value = value
        self.log(message='           final_value (1) updated to    = {}   (type={})'.format( final_value, type(final_value) ), level='debug')
        log_indent = ''
        if log_indent_spaces > 0:
            for i in range(0, log_indent_spaces):
                log_indent = '{} '.format(log_indent)
        if value is None:
            if set_default_when_not_present is True or set_default_when_null is True:
                final_value = default_val
                self.log(message='           final_value (2) updated to    = {}   (type={})'.format( final_value, type(final_value) ), level='debug')
            else:
                raise Exception('{} value for field "{}" was NoneType or not present'.format(value_type, spec_path))
        if isinstance(final_value, value_type) is False:
            if set_default_when_type_mismatch is True:
                final_value = None
                self.log(message='           final_value (3) updated to    = {}   (type={})'.format( final_value, type(final_value) ), level='debug')
            else:
                raise Exception('{} value for field "{}" was expected to be a string but found "{}"'.format(value_type, spec_path, type(value)))
        else:
            if value is None and set_default_when_null is True:
                final_value = default_val
                self.log(message='           final_value (4) updated to    = {}   (type={})'.format( final_value, type(final_value) ), level='debug')
            elif value is None and set_default_when_null is False:
                raise Exception('Value was NoneType and set_default_when_null is False')
        if raise_exception_when_empty is True:
            if len(final_value) == 0:
                raise Exception('{} value for field "{}" was zero length'.format(value_type, spec_path))
        self.log(message='{}Spec path "{}" validated'.format(log_indent, spec_path), level='info')
        return final_value

    def _validate(self, variable_cache: VariableCache=VariableCache()):
        if self.spec is None:
            self.spec = dict()
        if isinstance(self.spec, dict) is False:
            self.spec = dict()

        if variable_cache.get_value(
            variable_name='{}:validated'.format(self._var_name()),
            value_if_expired=False,
            default_value_if_not_found=False,
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        ) is False:

            self.log(message='Not Yet Validated', level='debug')

            validation_config_for_string_and_list_fields = {
                'description': {
                    'default_val': '',
                    'value_type': str,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': False,

                },
                'kind': {
                    'default_val': None,
                    'value_type': str,
                    'set_default_when_not_present': False,
                    'set_default_when_type_mismatch': False,
                    'set_default_when_null': False,
                    'raise_exception_when_empty': False,
                },
                'version': {
                    'default_val': None,
                    'value_type': str,
                    'set_default_when_not_present': False,
                    'set_default_when_type_mismatch': False,
                    'set_default_when_null': False,
                    'raise_exception_when_empty': False,
                },
                'versionChangelog': {
                    'default_val': '> **Note**\n> No changelog provided\n\n',
                    'value_type': str,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': False,
                },
                'baseClass': {
                    'default_val': 'ManifestBase',
                    'value_type': str,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': False,
                },
                'supportedVersions': {
                    'default_val': list(),
                    'value_type': list,
                    'set_default_when_not_present': False,
                    'set_default_when_type_mismatch': False,
                    'set_default_when_null': False,
                    'raise_exception_when_empty': True,
                },
                'importStatements': {
                    'default_val': ['from py_animus.manifest_management import *', 'from py_animus import get_logger', 'import traceback',],
                    'value_type': list,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': True,
                },
                'specFields': {
                    'default_val': list(),
                    'value_type': list,
                    'set_default_when_not_present': False,
                    'set_default_when_type_mismatch': False,
                    'set_default_when_null': False,
                    'raise_exception_when_empty': True,
                },
                'additionalExamples': {
                    'default_val': [
                        {
                            'exampleName': 'minimal',
                            'manifest': {
                                'generated': True,
                            },
                            'explanatoryText': 'This is the absolute minimal example based on required values. Dummy random data was generated where required.'
                        }
                    ],
                    'value_type': list,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': True,
                },
            }

            validation_specFields_for_string_and_list_fields = {
                'fieldName': {
                    'default_val': None,
                    'value_type': str,
                    'set_default_when_not_present': False,
                    'set_default_when_type_mismatch': False,
                    'set_default_when_null': False,
                    'raise_exception_when_empty': True,

                },
                'fieldDescription': {
                    'default_val': '',
                    'value_type': str,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': False,

                },
                'fieldType': {
                    'default_val': None,
                    'value_type': str,
                    'set_default_when_not_present': False,
                    'set_default_when_type_mismatch': False,
                    'set_default_when_null': False,
                    'raise_exception_when_empty': True,

                },
                'fieldRequired': {
                    'default_val': False,
                    'value_type': bool,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': False,

                },
                'fieldDefaultValue': {
                    'default_val': None,
                    'value_type': object,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': False,

                },
                'customValidation': {
                    'default_val': 'pass',
                    'value_type': str,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': True,

                },
                'fieldSetDefaultValueConditions': {
                    'default_val': [
                        { 'fieldDefinitionNotPresentInManifest': True },
                        { 'fieldValueTypeMismatch'             : True },
                        { 'fieldValueIsNull'                   : True },
                    ],
                    'value_type': list,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': True,

                },
            }

            validation_additionalExamples_for_string_and_list_fields = {
                'exampleName': {
                    'default_val': None,
                    'value_type': str,
                    'set_default_when_not_present': False,
                    'set_default_when_type_mismatch': False,
                    'set_default_when_null': False,
                    'raise_exception_when_empty': False,

                },
                'manifest': {
                    'default_val': {'generated': True},
                    'value_type': dict,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': True,

                },
                'explanatoryText': {
                    'default_val': 'This is the absolute minimal example based on required values. Dummy random data was generated where required.',
                    'value_type': str,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': True,

                },
            }

            validation_additionalExamples_manifest_for_string_and_list_fields = {
                'generated': {
                    'default_val': False,
                    'value_type': bool,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': False,
                },
                'specData': {
                    'default_val': None,
                    'value_type': str,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': False,
                },
                'additionalMetadata': {
                    'default_val': '',
                    'value_type': str,
                    'set_default_when_not_present': True,
                    'set_default_when_type_mismatch': True,
                    'set_default_when_null': True,
                    'raise_exception_when_empty': False,
                },
            }

            for spec_str_field, params in validation_config_for_string_and_list_fields.items():
                self.spec[spec_str_field] = self._validate_str_or_list_or_boolean(
                    spec_path=spec_str_field,
                    value=find_key(dot_notation_path=spec_str_field, payload=self.spec),
                    value_type=params['value_type'],
                    default_val=params['default_val'],
                    set_default_when_not_present=params['set_default_when_not_present'],
                    set_default_when_type_mismatch=params['set_default_when_type_mismatch'],
                    set_default_when_null=params['set_default_when_null'],
                    raise_exception_when_empty=params['raise_exception_when_empty']
                )

            final_specFields_list = list()
            for spec_field_dict in find_key(dot_notation_path='specFields', payload=self.spec):
                self.log(message='---------- Validating specField "{}" ----------'.format(spec_field_dict['fieldName']), level='info')
                conditions_found = 0
                for spec_str_field, params in validation_specFields_for_string_and_list_fields.items():
                    self._validate_str_or_list_or_boolean(
                        spec_path=spec_str_field,
                        value=find_key(dot_notation_path=spec_str_field, payload=spec_field_dict),
                        value_type=params['value_type'],
                        default_val=params['default_val'],
                        set_default_when_not_present=params['set_default_when_not_present'],
                        set_default_when_type_mismatch=params['set_default_when_type_mismatch'],
                        set_default_when_null=params['set_default_when_null'],
                        raise_exception_when_empty=params['raise_exception_when_empty'],
                        log_indent_spaces=3
                    )

                    if spec_str_field == 'fieldSetDefaultValueConditions':
                        if spec_str_field in spec_field_dict:
                            conditions = spec_field_dict[spec_str_field]
                            self.log(message='        conditions={}'.format(conditions), level='debug')
                            for condition in conditions:
                                for key in ('fieldDefinitionNotPresentInManifest', 'fieldValueTypeMismatch', 'fieldValueIsNull',):
                                    if key in condition:
                                        try:
                                            if isinstance(condition[key], bool) is False:
                                                raise Exception('{} field in spec.specFields.[].fieldSetDefaultValueConditions must be a boolean'.format(key))
                                            conditions_found += 1
                                        except:
                                            pass
                if conditions_found != 3:
                    raise Exception('When spec.specFields.[].fieldSetDefaultValueConditions is supplied, all three fields of fieldDefinitionNotPresentInManifest, fieldValueTypeMismatch, fieldValueIsNull must also be supplied.')
                final_specFields_list.append(spec_field_dict)


            minimal_override = False
            final_examples_list = list()
            for spec_field_dict in find_key(dot_notation_path='additionalExamples', payload=self.spec):
                # self.log(message='   spec_field_dict={}'.format(spec_field_dict), level='debug')
                self.log(message='---------- Validating additionalExamples "{}" ----------'.format(spec_field_dict['exampleName']), level='info')
                if spec_field_dict['exampleName'] == 'minimal':
                    minimal_override = True
                for spec_str_field, params in validation_additionalExamples_for_string_and_list_fields.items():
                    self._validate_str_or_list_or_boolean(
                        spec_path=spec_str_field,
                        value=find_key(dot_notation_path=spec_str_field, payload=spec_field_dict),
                        value_type=params['value_type'],
                        default_val=params['default_val'],
                        set_default_when_not_present=params['set_default_when_not_present'],
                        set_default_when_type_mismatch=params['set_default_when_type_mismatch'],
                        set_default_when_null=params['set_default_when_null'],
                        raise_exception_when_empty=params['raise_exception_when_empty'],
                        log_indent_spaces=3
                    )

                    if spec_str_field == 'manifest':
                        self.log(message='      ~~~ Validating Example Manifest Definition ~~~', level='info')
                        for spec_str_field2, params2 in validation_additionalExamples_manifest_for_string_and_list_fields.items():
                            self._validate_str_or_list_or_boolean(
                                spec_path=spec_str_field2,
                                value=find_key(dot_notation_path=spec_str_field2, payload=spec_field_dict['manifest']),
                                value_type=params2['value_type'],
                                default_val=params2['default_val'],
                                set_default_when_not_present=params2['set_default_when_not_present'],
                                set_default_when_type_mismatch=params2['set_default_when_type_mismatch'],
                                set_default_when_null=params2['set_default_when_null'],
                                raise_exception_when_empty=params2['raise_exception_when_empty'],
                                log_indent_spaces=6
                            )
                final_examples_list.append(spec_field_dict)

            if minimal_override is False:
                final_examples_list.append(
                    {
                        'exampleName': 'minimal',  # This will also be used to compile the the value of metadata.name
                        'manifest':{
                            'generated': True, # This will automatically generate an example spec data with the minimum required fields and default values
                            'additionalMetadata': 'skipDeleteAll: true',
                        },
                        'explanatoryText': 'This is the absolute minimal example based on required values. Dummy random data was generated where required.'
                    }
                )

            self.log(message='final_examples_list={}'.format(final_examples_list), level='debug')
            if len(final_examples_list) == 0:
                raise Exception('At least one example definition must be supplied')

            self.spec['specFields'] = copy.deepcopy(final_specFields_list)
            self.spec['additionalExamples'] = copy.deepcopy(final_examples_list)

            self.log(message='Spec Validated', level='debug')
        else:
            self.log(message='Already Validated', level='debug')

        variable_cache.store_variable(variable=Variable(name='{}:validated'.format(self._var_name()),logger=self.logger, initial_value=True), overwrite_existing=True)

    def _determine_directory_actions(self, directory: str, existing_actions: list, command: str, do_not_delete_recursively: bool= True)->list:
        actions = copy.deepcopy(existing_actions)
        d_path = Path(directory)
        if d_path.exists() is False:
            if command == 'delete':
                self.log(message='Directory {} not found - no action required'.format(directory), level='info')
            elif command == 'apply':
                self.log(message='Directory {} not found - create_dir action recorded'.format(directory), level='info')
                actions.append({'create_dir': directory})
            else:
                self.log(message='Directory {} not found - command not recognized - NO ACTIONS'.format(directory), level='warning')
        else:
            if command == 'delete':
                if do_not_delete_recursively is False:
                    self.log(message='Directory {} found - delete_dir_recursively action recorded'.format(directory), level='info')
                    actions.append({'delete_dir_recursively': directory})
                else:
                    self.log(message='Directory {} found - no action required because do_not_delete_recursively is True'.format(directory), level='info')
            elif command == 'apply':
                self.log(message='Directory {} found - no action required'.format(directory), level='info')
            else:
                self.log(message='Directory {} found - command not recognized - NO ACTIONS'.format(directory), level='warning')
        return actions

    def _determine_file_actions(self, file: str, existing_actions: list, command: str, action_command: str)->list:
        actions = copy.deepcopy(existing_actions)
        file_path_object = Path(file)
        if file_path_object.exists() is False:
            if command == 'delete':
                self.log(message='File {} not found - no action required'.format(file), level='info')
            elif command == 'apply':
                self.log(message='File {} not found - {} action recorded'.format(file, action_command), level='info')
                actions.append({action_command: file})
            else:
                self.log(message='File {} not found - command not recognized - NO ACTIONS'.format(file), level='warning')
        else:
            if command == 'delete':
                self.log(message='File {} found - {} action recorded'.format(file, action_command), level='info')
                actions.append({action_command: file})
            elif command == 'apply':
                self.log(message='File {} found - no action required'.format(file), level='info')
            else:
                self.log(message='File {} found - command not recognized - NO ACTIONS'.format(file), level='warning')
        return actions

    def _determine_output_filename(self, file_name_no_extension: str, base_dir: str, component: str, output_file_extension: str, additional_sub_dir: str=None)->str:
        file_name = '{}{}{}.{}'.format(
            base_dir,
            os.sep,
            file_name_no_extension,
            output_file_extension
        )
        if additional_sub_dir is not None:
            file_name = '{}{}{}{}{}.{}'.format(
                base_dir,
                os.sep,
                additional_sub_dir,
                os.sep,
                file_name_no_extension,
                output_file_extension
            )
        if 'outputPaths' in self.spec:
            if component in self.spec['outputPaths']:
                file_name = '{}{}{}.{}'.format(
                    self.spec['outputPaths'][component],
                    os.sep,
                    file_name_no_extension,
                    output_file_extension
                )
                if additional_sub_dir is not None:
                    file_name = '{}{}{}{}{}.{}'.format(
                        self.spec['outputPaths'][component],
                        os.sep,
                        additional_sub_dir,
                        os.sep,
                        file_name_no_extension,
                        output_file_extension
                    )
                self.log(message='Default {} output file was overridden with spec.outputPaths.doc - file_name="{}"'.format(component, file_name), level='info')
            else:
                self.log(message='Default {} output file used (2) - file_name="{}"'.format(component, file_name), level='info')
        else:
            self.log(message='Default {} output file used (1) - file_name="{}"'.format(component, file_name), level='info')
        return file_name

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders())->bool:
        self._validate(variable_cache=variable_cache)
        command = variable_cache.get_value(variable_name='{}:command'.format(self._var_name()))

        self.log(message='----------------------- running implemented_manifest_differ_from_this_manifest() ----------------------', level='info')
        self.log(message='spec as JSON: {}'.format(json.dumps(self.spec)), level='debug')

        actions = list()

        ###
        ### Check Directories
        ###

        dirs = list()
        if 'outputPaths' in self.spec:
            if 'doc' in self.spec['outputPaths']:
                self.log(message='Default DOC_BASE_PATH was overridden with spec.outputPaths.doc - value="{}"'.format(self.spec['outputPaths']['doc']), level='info')
                dirs.append(self.spec['outputPaths']['doc'])
            else:
                self.log(message='Default DOC_BASE_PATH used - value="{}"'.format(DOC_BASE_PATH), level='info')
                dirs.append(DOC_BASE_PATH)
            if 'implementations' in self.spec['outputPaths']:
                self.log(message='Default IMPLEMENTATIONS_BASE_PATH was overridden with spec.outputPaths.implementations - value="{}"'.format(self.spec['outputPaths']['implementations']), level='info')
                dirs.append(self.spec['outputPaths']['implementations'])
            else:
                self.log(message='Default IMPLEMENTATIONS_BASE_PATH used - value="{}"'.format(IMPLEMENTATIONS_BASE_PATH), level='info')
                dirs.append(IMPLEMENTATIONS_BASE_PATH)
        else:
            dirs = (DOC_BASE_PATH, IMPLEMENTATIONS_BASE_PATH,)
        for d in dirs:
            actions = self._determine_directory_actions(
                directory=d,
                existing_actions=actions,
                command=command
            )

        dirs = list()
        examples_dir = '{}{}{}'.format(EXAMPLES_BASE_PATH, os.sep, self.metadata['name'])
        if 'outputPaths' in self.spec:
            if 'examples' in self.spec['outputPaths']:
                examples_dir = self.spec['outputPaths']['examples']
                self.log(message='Default EXAMPLES_BASE_PATH was overridden with spec.outputPaths.examples - value="{}"'.format(self.spec['outputPaths']['examples']), level='info')
                dirs.append(self.spec['outputPaths']['examples'])
            else:
                self.log(message='Default EXAMPLES_BASE_PATH used (2) - value="{}"'.format(EXAMPLES_BASE_PATH), level='info')
                dirs.append(examples_dir)
        else:
            self.log(message='Default EXAMPLES_BASE_PATH used (1) - value="{}"'.format(EXAMPLES_BASE_PATH), level='info')
        for d in dirs:
            actions = self._determine_directory_actions(
                directory=d,
                existing_actions=actions,
                command=command,
                do_not_delete_recursively=False
            )

        if 'additionalExamples' in self.spec:
            for additional_example_data in self.spec['additionalExamples']:
                for field, value in additional_example_data.items():
                    if field == 'exampleName':
                        additional_example_directory = '{}{}{}'.format(
                            examples_dir,
                            os.sep,
                            value
                        )
                        actions = self._determine_directory_actions(
                            directory=additional_example_directory,
                            existing_actions=actions,
                            command=command,
                            do_not_delete_recursively=False
                        )
        else:
            self.log(message='No additionalExamples found in spec (1)', level='warning')

        ###
        ### Implementation File Actions
        ###
        file_name = self._determine_output_filename(file_name_no_extension=self.metadata['name'], base_dir=IMPLEMENTATIONS_BASE_PATH, component='implementations', output_file_extension='py', additional_sub_dir=None)

        action_command = 'no-action'
        if command == 'delete':
            action_command = 'delete_implementation_file'
        if command == 'apply':
            action_command = 'create_implementation_file'
        actions = self._determine_file_actions(
            file=file_name,
            existing_actions=actions,
            command=command,
            action_command=action_command
        )

        ###
        ### Documentation File Actions
        ###
        file_name = self._determine_output_filename(file_name_no_extension=self.metadata['name'], base_dir=DOC_BASE_PATH, component='doc', output_file_extension='md', additional_sub_dir=None)

        action_command = 'no-action'
        if command == 'delete':
            action_command = 'delete_documentation_file'
        if command == 'apply':
            action_command = 'create_documentation_file'
        actions = self._determine_file_actions(
            file=file_name,
            existing_actions=actions,
            command=command,
            action_command=action_command
        )

        ###
        ### Example Files
        ###
        if 'additionalExamples' in self.spec:
            for additional_example_data in self.spec['additionalExamples']:
                for field, value in additional_example_data.items():
                    if field == 'exampleName':
                        if value != 'minimal':
                            file_name = self._determine_output_filename(file_name_no_extension='example', base_dir=examples_dir, component='examples', output_file_extension='yaml', additional_sub_dir=value)
                            action_command = 'no-action'
                            if command == 'delete':
                                action_command = 'delete_example_file'
                            if command == 'apply':
                                action_command = 'create_example_file'
                            actions = self._determine_file_actions(
                                file=file_name,
                                existing_actions=actions,
                                command=command,
                                action_command=action_command
                            )
                            variable_cache.store_variable(variable=Variable(name='{}:example.{}.file'.format(self._var_name(), value), initial_value=copy.deepcopy(file_name), logger=self.logger), overwrite_existing=True)
        else:
            self.log(message='No additionalExamples found in spec (1)', level='warning')
        file_name = self._determine_output_filename(file_name_no_extension='example', base_dir=examples_dir, component='examples', output_file_extension='yaml', additional_sub_dir='minimal')
        variable_cache.store_variable(variable=Variable(name='{}:example.minimal.file'.format(self._var_name()), initial_value=copy.deepcopy(file_name), logger=self.logger), overwrite_existing=True)

        file_name = self._determine_output_filename(file_name_no_extension='example', base_dir=examples_dir, component='examples', output_file_extension='yaml', additional_sub_dir='minimal')
        action_command = 'no-action'
        if command == 'delete':
            action_command = 'delete_example_file'
        if command == 'apply':
            action_command = 'create_example_file'
        actions = self._determine_file_actions(
            file=file_name,
            existing_actions=actions,
            command=command,
            action_command=action_command
        )


        ###
        ### DONE
        ###
        self.log(message='** spec as JSON: {}'.format(json.dumps(self.spec)), level='debug')

        self.log(message='-------------------- DONE running implemented_manifest_differ_from_this_manifest() --------------------', level='info')
        variable_cache.store_variable(variable=Variable(name='{}:actions'.format(self._var_name()),initial_value=actions,ttl=-1,logger=self.logger,mask_in_logs=False),overwrite_existing=False)
        if len(actions) > 0:
            return True

        return False

    def _action_create_dir(self, directory_name: str):
        self.log(message='      ACTION: Creating directory: {}'.format(directory_name), level='info')
        Path( directory_name ).mkdir( parents=True, exist_ok=True )

    def _action_delete_dir_recursively(self, directory_name: str):
        self.log(message='      ACTION: Recursively deleting directory: {}'.format(directory_name), level='info')
        succeeded = False
        try:
            os.remove(directory_name)
            succeeded = True
        except:
            self.log(message='EXCEPTION: {}'.format(traceback.format_exc()), level='error')
        try:
            shutil.rmtree(directory_name)
            succeeded = True
        except:
            self.log(message='EXCEPTION: {}'.format(traceback.format_exc()), level='error')
        if succeeded is False:
            # raise Exception('Failed to recursively delete directory "{}"'.format(directory_name))
            self.log(message='Failed to recursively delete directory "{}" - manual action may be required'.format(directory_name), level='warning')

    def _action_create_implementation_file(self, file_name: str):
        self.log(message='      ACTION: Creating Implementation File: {}'.format(file_name), level='info')
        my_path = inspect.getfile(self.__class__)
        self.log(message='         Running from file: {}'.format(my_path), level='debug')
        source_file = os.sep.join(my_path.split(os.sep)[0:10])
        source_file = '{}{}implementations{}source.py'.format(
            source_file,
            os.sep,
            os.sep
        )
        self.log(message='         Loading Source Template from file: {}'.format(source_file), level='info')
        data = ''
        with open(source_file, 'r') as rf:
            data = rf.read()
        self.log(message='         Performing variable substitutions', level='info')

        imports_text = ''
        import_statements = list()
        if 'importStatements' not in self.spec:
            import_statements = ['from py_animus.manifest_management import *', 'from py_animus import get_logger', 'import traceback',]
        else:
            import_statements = self.spec['importStatements']
        for import_line in import_statements:
            imports_text = '{}\n{}'.format(imports_text,import_line)
        imports_text = '{}\n\n'.format(imports_text)

        data = data.replace('__IMPORTS__', imports_text)
        data = data.replace('__KIND__', self.spec['kind'])
        data = data.replace('__BASE_CLASS__', self.spec['baseClass'])
        data = data.replace('__IMPLEMENTATION_DESCRIPTION__', self.spec['description'])
        data = data.replace('__VERSION__', self.spec['version'])
        data = data.replace('__SUPPORTED_VERSIONS__', '{}'.format(self.spec['supportedVersions']))
        self.log(message='         Writing data to target file: {}'.format(file_name), level='info')
        with open(file_name, 'w') as wf:
            wf.write(data)

    def _action_delete_implementation_file(self, file_name: str):
        self.log(message='      ACTION: Deleting Implementation File: {}'.format(file_name), level='info')
        os.unlink(file_name)

    def _action_create_documentation_file(self, file_name: str, variable_cache: VariableCache=VariableCache()):
        self.log(message='      ACTION: Creating Documentation File: {}'.format(file_name), level='info')
        self.log(message='         variable_cache as JSON: {}'.format(json.dumps(variable_cache.to_dict())), level='info')
        my_path = inspect.getfile(self.__class__)
        self.log(message='         Running from file: {}'.format(my_path), level='debug')
        source_file = os.sep.join(my_path.split(os.sep)[0:10])
        source_file = '{}{}doc{}extension-template.md'.format(
            source_file,
            os.sep,
            os.sep
        )
        self.log(message='          Loading Source Template from file: {}'.format(source_file), level='info')

        ###
        ### COMMON FIELDS
        ###
        data = ''
        with open(source_file, 'r') as rf:
            data = rf.read()
        self.log(message='         Performing variable substitutions', level='info')
        data = data.replace('__KIND__', self.spec['kind'])
        data = data.replace('__DESCRIPTION__', self.spec['description'])
        data = data.replace('__EXTENSION_NAME__', self.metadata['name'])
        data = data.replace('__VERSION__', self.spec['version'])

        ###
        ### FIELD TABLE
        ###
        field_required_value_map = {
            True: 'Yes',
            False: 'No',
        }
        field_rows_text = ''
        for field_data in self.spec['specFields']:
            field_description = '{}'.format(field_data['fieldDescription'])
            field_description = field_description.replace('\n', '')
            field_description = field_description.replace('\r', '')
            field_description = field_description.strip()

            field_rows_text = '{}| `{}` | {} | {} | {} | {} |\n'.format(
                field_rows_text,
                field_data['fieldName'],
                field_data['fieldType'],
                field_required_value_map[field_data['fieldRequired']],
                self.spec['version'],
                field_description
            )
        data = data.replace('__TABLE_ROWS__', field_rows_text)


        ###
        ### EXAMPLES
        ###

        examples_lines = ''
        example_template = '''## Example: __EXAMPLE_NAME__

```shell
export SCENARIO_NAME="__EXAMPLE_NAME__"
```

Example manifest: [__EXAMPLE_MANIFEST_FILE_NAME__](__PATH_TO_EXAMPLE_MANIFEST__)

```yaml
___EXAMPLE_MANIFEST__
```

__EXAMPLE_DESCRIPTION__
        '''
        minimal_example_override = False
        if 'additionalExamples' in self.spec:
            for additional_example_data in self.spec['additionalExamples']:
                example_text = copy.deepcopy(example_template)
                example_name = additional_example_data['exampleName']
                self.log(message='            Processing example named: {}'.format(example_name), level='info')
                if example_name == 'minimal':
                    minimal_example_override = True
                    self.log(message='               Minimal example will be used from Manifest definition', level='info')
                    var_name = '{}:example.{}.file'.format(self._var_name(), example_name)
                    self.log(message='                  Looking up variable "{}"'.format(var_name), level='info')
                example_file = variable_cache.get_value(
                    variable_name='{}:example.{}.file'.format(self._var_name(), example_name),
                    value_if_expired=None,
                    raise_exception_on_expired=False,
                    raise_exception_on_not_found=False,
                    default_value_if_not_found=None,
                    for_logging=False
                )
                self.log(message='               example_file={}'.format(example_file), level='info')
                if example_file is not None:
                    example_text = example_text.replace('__EXAMPLE_NAME__', example_name)
                    example_text = example_text.replace('__PATH_TO_EXAMPLE_MANIFEST__', example_file)
                    example_text = example_text.replace('__EXAMPLE_MANIFEST_FILE_NAME__', example_file.split(os.sep)[-1])
                    example_text = example_text.replace('__EXAMPLE_DESCRIPTION__', additional_example_data['explanatoryText'])
                    if os.path.exists(example_file):
                        with open(example_file, 'r') as exmf:
                            example_text = example_text.replace('___EXAMPLE_MANIFEST__', exmf.read())
                    else:
                        example_text = example_text.replace('___EXAMPLE_MANIFEST__', '# NO EXAMPLE FILE FOUND...')
                    examples_lines = '{}\n\n{}'.format(
                        examples_lines,
                        example_text
                    )
                    self.log(message='               len(examples_lines)={}'.format(len(examples_lines)), level='info')
        if minimal_example_override is False:
            example_text = copy.deepcopy(example_template)
            example_name = 'minimal'
            example_file = variable_cache.get_value(
                variable_name='{}:example.minimal.file'.format(self._var_name(), example_name),
                value_if_expired=None,
                raise_exception_on_expired=False,
                raise_exception_on_not_found=False,
                default_value_if_not_found=None,
                for_logging=False
            )
            if example_file is not None:
                example_text = example_text.replace('__EXAMPLE_NAME__', example_name)
                example_text = example_text.replace('__PATH_TO_EXAMPLE_MANIFEST__', example_file)
                example_text = example_text.replace('__EXAMPLE_MANIFEST_FILE_NAME__', example_file.split(os.sep)[-1])
                example_text = example_text.replace('__EXAMPLE_DESCRIPTION__', 'This is a simple minimal example for this manifest kind')
                if os.path.exists(example_file):
                    with open(example_file, 'r') as exmf:
                        example_text = example_text.replace('___EXAMPLE_MANIFEST__', exmf.read())
                else:
                    example_text = example_text.replace('___EXAMPLE_MANIFEST__', '# NO EXAMPLE FILE FOUND...')
                examples_lines = '{}\n\n{}'.format(
                    examples_lines,
                    example_text
                )

        data = data.replace('__PER_SCENARIO_EXAMPLE__', examples_lines)


        ###
        ### DONE
        ###
        self.log(message='         Writing data to target file: {}'.format(file_name), level='info')
        with open(file_name, 'w') as wf:
            wf.write(data)

    def _action_delete_documentation_file(self, file_name: str):
        self.log(message='      ACTION: Deleting Documentation File: {}'.format(file_name), level='info')
        os.unlink(file_name)

    def _action_create_example_file(self, file_name: str, variable_cache: VariableCache=VariableCache()):
        example_name = file_name.split(os.sep)[-2]
        self.log(message='      ACTION: Creating Example "{}" File: {}'.format(example_name, file_name), level='info')
        variable_cache.store_variable(
            variable=Variable(
                name='{}:example.{}.file'.format(self._var_name(), example_name),
                initial_value=copy.deepcopy(file_name),
                logger=self.logger
            ),
            overwrite_existing=True
        )

        base_template_data = dict()
        base_template_data['kind'] = self.spec['kind']
        base_template_data['version'] = self.spec['version']
        base_template_data['metadata'] = dict()
        base_template_data['metadata']['name'] = '{}-{}'.format(self.metadata['name'], example_name)
        final_template_data = dict()

        # FIXME When a field is required, but has no default value, set some possible value appropriate to the type.
        for example_data in self.spec['additionalExamples']:
            if example_data['exampleName'] == example_name:
                self.log(message='         Processing Data for "{}"'.format(example_name), level='debug')
                generated = True
                if 'generated' in example_data['manifest']:
                    generated = example_data['manifest']['generated']
                template_data = copy.deepcopy(base_template_data)
                if generated is True:
                    for spec_field in self.spec['specFields']:
                        if spec_field['fieldDefaultValue'] is not None and spec_field['fieldRequired'] is True:
                            if 'spec' not in template_data:
                                template_data['spec'] = dict()
                            template_data['spec'][spec_field['fieldName']] = spec_field['fieldDefaultValue']
                        elif spec_field['fieldDefaultValue'] is None and spec_field['fieldRequired'] is True:
                            if 'spec' not in template_data:
                                template_data['spec'] = dict()
                            template_data['spec'][spec_field['fieldName']] = 'a-value-of-type-{}'.format(spec_field['fieldType'])
                if 'specData' in example_data['manifest']:
                    spec_data_as_dict = parse_raw_yaml_data(yaml_data=example_data['manifest']['specData'], logger=self.logger)
                    if spec_data_as_dict is not None:
                        if isinstance(spec_data_as_dict, dict):
                            if len(spec_data_as_dict) > 0:
                                if 'spec' not in template_data:
                                    template_data['spec'] = dict()
                                for part, part_data in spec_data_as_dict.items():
                                    for k,v in part_data.items():
                                        template_data['spec'][k] = v
                if 'additionalMetadata' in example_data['manifest']:
                    additional_metadata_as_dict = parse_raw_yaml_data(yaml_data=example_data['manifest']['additionalMetadata'], logger=self.logger)
                    if additional_metadata_as_dict is not None:
                        if isinstance(additional_metadata_as_dict, dict):
                            if len(additional_metadata_as_dict) > 0:
                                for part, part_data in additional_metadata_as_dict.items():
                                    for k,v in part_data.items():
                                        template_data['metadata'][k] = v
                # Normalize the the template_data by converted dotted notation fields to proper complex data structures.
                output_data = dict()
                for t_field_name, t_field_data in template_data.items():
                    if isinstance(t_field_data, dict):
                        converted_t_field_data = dict()
                        for field_name, field_data in t_field_data.items():
                            root_field = create_field(dotted_name=field_name, value=copy.deepcopy(field_data))
                            for k,v in root_field.to_dict().items():
                                if k not in converted_t_field_data:
                                    converted_t_field_data[k] = v
                                else:
                                    if isinstance(v, dict):
                                        converted_t_field_data[k] = merge_dicts(A=converted_t_field_data[k], B=v)
                                    else:
                                        converted_t_field_data[k] = v
                        output_data[t_field_name] = converted_t_field_data
                    else:
                        output_data[t_field_name] = t_field_data
                final_template_data = copy.deepcopy(output_data)
                self.log(message='             final_template_data as JSON: {}'.format(json.dumps(final_template_data)), level='info')

        if len(final_template_data) > 0:
            with open(file_name, "w") as f:
                f.write(yaml.dump(final_template_data))

    def _action_delete_example_file(self, file_name: str):
        example_name = file_name.split(os.sep)[-2]
        self.log(message='      ACTION: Deleting Example "{}" File: {}'.format(example_name, file_name), level='info')
        os.unlink(file_name)

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        variable_cache.store_variable(variable=Variable(name='{}:command'.format(self._var_name()),initial_value='apply',ttl=-1,logger=self.logger,mask_in_logs=False),overwrite_existing=False)
        self.log(message='APPLY CALLED', level='info')
        if self.implemented_manifest_differ_from_this_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache) is False:
            self.log(message='No changes detected', level='info')
            return
        actions = variable_cache.get_value(variable_name='{}:actions'.format(self._var_name()), value_if_expired=list(), raise_exception_on_expired=False, raise_exception_on_not_found=False,default_value_if_not_found=list(), for_logging=False)
        self.log(message='actions : {}'.format(actions), level='debug')
        self.log(message='Applying Manifest', level='info')
        self.log(message='   Implementation Name           : {}'.format(self.metadata['name']), level='info')

        ###
        ### Create Directories
        ###
        remaining_actions = list()
        for action in actions:
            for action_name, action_data in action.items():
                if action_name == 'create_dir':
                    self._action_create_dir(directory_name=action_data)
                else:
                    remaining_actions.append(copy.deepcopy(action))
        actions = copy.deepcopy(remaining_actions)
        remaining_actions = list()

        ###
        ### Prepare Initial Source File
        ###
        remaining_actions = list()
        for action in actions:
            for action_name, action_data in action.items():
                if action_name == 'create_implementation_file':
                    self._action_create_implementation_file(file_name=action_data)
                else:
                    remaining_actions.append(copy.deepcopy(action))
        actions = copy.deepcopy(remaining_actions)

        ###
        ### Prepare Example Manifest
        ###
        remaining_actions = list()
        for action in actions:
            for action_name, action_data in action.items():
                if action_name == 'create_example_file':
                    self._action_create_example_file(file_name=action_data, variable_cache=variable_cache)
                else:
                    remaining_actions.append(copy.deepcopy(action))
        actions = copy.deepcopy(remaining_actions)

        ###
        ### Prepare Documentation
        ###
        remaining_actions = list()
        for action in actions:
            for action_name, action_data in action.items():
                if action_name == 'create_documentation_file':
                    self._action_create_documentation_file(file_name=action_data, variable_cache=variable_cache)
                else:
                    remaining_actions.append(copy.deepcopy(action))
        actions = copy.deepcopy(remaining_actions)

        ###
        ### DONE
        ###
        if len(remaining_actions) > 0:
            self.log(message='Actions left over: {}'.format(remaining_actions), level='error')

        variable_cache.delete_variable(variable_name='{}:command'.format(self._var_name()))
        variable_cache.delete_variable(variable_name='{}:actions'.format(self._var_name()))
        variable_cache.store_variable(variable=Variable(name='{}'.format(self._var_name()),initial_value=True,ttl=-1,logger=self.logger,mask_in_logs=False),overwrite_existing=False)
        return

    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        variable_cache.store_variable(variable=Variable(name='{}:command'.format(self._var_name()),initial_value='delete',ttl=-1,logger=self.logger,mask_in_logs=False),overwrite_existing=False)
        self.log(message='DELETE CALLED', level='info')
        if self.implemented_manifest_differ_from_this_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache) is False:
            self.log(message='No changes detected', level='info')
            return
        actions = variable_cache.get_value(variable_name='{}:actions'.format(self._var_name()), value_if_expired=list(), raise_exception_on_expired=False, raise_exception_on_not_found=False,default_value_if_not_found=list(), for_logging=False)
        self.log(message='Deleting Manifest', level='info')
        self.log(message='   Implementation Name           : {}'.format(self.metadata['name']), level='info')

        ###
        ### Delete Source File
        ###
        remaining_actions = list()
        for action in actions:
            for action_name, action_data in action.items():
                if action_name == 'delete_implementation_file':
                    self._action_delete_implementation_file(file_name=action_data)
                else:
                    remaining_actions.append(copy.deepcopy(action))
        actions = copy.deepcopy(remaining_actions)

        ###
        ### Delete Documentation
        ###
        remaining_actions = list()
        for action in actions:
            for action_name, action_data in action.items():
                if action_name == 'delete_documentation_file':
                    self._action_delete_documentation_file(file_name=action_data)
                else:
                    remaining_actions.append(copy.deepcopy(action))
        actions = copy.deepcopy(remaining_actions)

        ###
        ### Delete Example Manifest
        ###
        remaining_actions = list()
        for action in actions:
            for action_name, action_data in action.items():
                if action_name == 'delete_example_file':
                    self._action_delete_example_file(file_name=action_data)
                else:
                    remaining_actions.append(copy.deepcopy(action))
        actions = copy.deepcopy(remaining_actions)

        ###
        ### Recursively Delete Directories
        ###
        remaining_actions = list()
        for action in actions:
            for action_name, action_data in action.items():
                if action_name == 'delete_dir_recursively':
                    self._action_delete_dir_recursively(directory_name=action_data)
                else:
                    remaining_actions.append(copy.deepcopy(action))

        ###
        ### DONE
        ###
        if len(remaining_actions) > 0:
            self.log(message='Actions left over: {}'.format(remaining_actions), level='error')

        variable_cache.delete_variable(variable_name=self._var_name())
        variable_cache.delete_variable(variable_name='{}:command'.format(self._var_name()))
        variable_cache.delete_variable(variable_name='{}:actions'.format(self._var_name()))
        return


if __name__ == '__main__':
    run_main()
