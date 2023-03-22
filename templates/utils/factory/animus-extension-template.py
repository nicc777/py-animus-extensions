from py_animus.manifest_management import *
from py_animus import get_logger
from py_animus.py_animus import run_main
import traceback
import os
from functools import reduce
import re
from typing import Any, Optional
import sys
from pathlib import Path


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
        log_indent = ''
        if log_indent_spaces > 0:
            for i in range(0, log_indent_spaces):
                log_indent = '{} '.format(log_indent)
        if value is None:
            if set_default_when_not_present is True or set_default_when_null is True:
                final_value = default_val
            else:
                raise Exception('{} value for field "{}" was NoneType or not present'.format(value_type, spec_path))
        if isinstance(value, value_type) is False:
            if set_default_when_type_mismatch is True:
                final_value = None
            else:
                raise Exception('{} value for field "{}" was expected to be a string but found "{}"'.format(value_type, spec_path, type(value)))
        else:
            final_value = value
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
                        {
                            'fieldDefinitionNotPresentInManifest': True,
                            'fieldValueTypeMismatch': True,
                            'fieldValueIsNull': True,
                        },
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
                    'default_val': None,
                    'value_type': str,
                    'set_default_when_not_present': False,
                    'set_default_when_type_mismatch': False,
                    'set_default_when_null': False,
                    'raise_exception_when_empty': True,
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
                for spec_str_field, params in validation_specFields_for_string_and_list_fields.items():
                    final_specFields_list.append(
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
                    )
                conditions_found = 0
                if spec_str_field == 'fieldSetDefaultValueConditions':
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


            final_additionalExamples_list = list()
            for spec_field_dict in find_key(dot_notation_path='additionalExamples', payload=self.spec):
                # self.log(message='   spec_field_dict={}'.format(spec_field_dict), level='debug')
                self.log(message='---------- Validating additionalExamples "{}" ----------'.format(spec_field_dict['exampleName']), level='info')
                for spec_str_field, params in validation_additionalExamples_for_string_and_list_fields.items():
                    final_additionalExamples_list.append(
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

            if len(final_additionalExamples_list) == 0:
                raise Exception('At least one example definition must be supplied')

            self.spec['specFields'] = copy.deepcopy(final_specFields_list)

            self.log(message='Spec Validated', level='debug')
        else:
            self.log(message='Already Validated', level='debug')

        variable_cache.store_variable(variable=Variable(name='{}:validated'.format(self._var_name()),logger=self.logger, initial_value=True), overwrite_existing=True)

    def _prep_file_path_variables(self, variable_cache: VariableCache=VariableCache()):
        variable_cache.store_variable(
            variable=Variable(
                name='{}:doc_file'.format(self._var_name()),
                initial_value='{}{}{}.md'.format(DOC_BASE_PATH, os.sep, self.metadata['name']),
                ttl=-1,
                logger=self.logger,
                mask_in_logs=False
            ),
            overwrite_existing=False
        )

        example_files = dict()
        for ex_data in self.spec['additionalExamples']:
            ex_name = ex_data['exampleName']
            ex_dir = '{}{}{}{}{}'.format(
                EXAMPLES_BASE_PATH,
                os.sep,
                self.metadata['name'],
                os.sep,
                ex_data['exampleName']
            )
            ex_file = '{}{}example.yaml'.format(
                ex_dir,
                os.sep
            )
            example_files[ex_name] = dict()
            example_files[ex_name]['directory'] = ex_dir
            example_files[ex_name]['file'] = ex_file
        variable_cache.store_variable(
            variable=Variable(
                name='{}:example_files'.format(self._var_name()),
                initial_value=example_files,
                ttl=-1,
                logger=self.logger,
                mask_in_logs=False
            ),
            overwrite_existing=False
        )

        variable_cache.store_variable(
            variable=Variable(
                name='{}:implementation_file'.format(self._var_name()),
                initial_value='{}{}{}.py'.format(IMPLEMENTATIONS_BASE_PATH, os.sep, self.metadata['name']),
                ttl=-1,
                logger=self.logger,
                mask_in_logs=False
            ),
            overwrite_existing=False
        )

    def _delete_file_path_variables(self, variable_cache: VariableCache=VariableCache()):
        variable_cache.delete_variable(variable_name='{}:doc_file'.format(self._var_name()))
        variable_cache.delete_variable(variable_name='{}:example_file'.format(self._var_name()))
        variable_cache.delete_variable(variable_name='{}:implementation_file'.format(self._var_name()))

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache())->bool:
        self._validate(variable_cache=variable_cache)
        self._prep_file_path_variables(variable_cache=variable_cache)
        command = variable_cache.get_value(variable_name='{}:command'.format(self._var_name()))
        
        actions = list()

        dirs = (DOC_BASE_PATH, IMPLEMENTATIONS_BASE_PATH)
        for d in dirs:
            d_path = Path(d)
            if d_path.exists() is False:
                if command == 'delete':
                    self.log(message='Directory {} not found - no action required'.format(d), level='info')
                else:
                    self.log(message='Directory {} not found - create_dir action recorded'.format(d), level='info')
                    actions.append({'create_dir': d})
            else:
                self.log(message='Directory {} found - no action required'.format(d), level='info')

        ex_dir = '{}{}{}'.format(
            EXAMPLES_BASE_PATH,
            os.sep,
            self.metadata['name']
        )
        d_path = Path(ex_dir)
        if d_path.exists() is False:
            if command == 'delete':
                self.log(message='Directory {} not found - no action required'.format(ex_dir), level='info')
            else:
                self.log(message='Directory {} not found - create_dir action recorded'.format(d), level='info')
                actions.append({'create_dir': d})
        else:
            if command == 'delete':
                self.log(message='Directory {} found - delete_dir_recursively action recorded'.format(ex_dir), level='info')
                actions.append({'delete_dir_recursively': ex_dir})
            else:
                self.log(message='Directory {} not found - no action required'.format(ex_dir), level='info')

        # files = (
        #     variable_cache.get_value(variable_name='{}:doc_file'.format(self._var_name())),
        #     variable_cache.get_value(variable_name='{}:example_file'.format(self._var_name())),
        #     variable_cache.get_value(variable_name='{}:implementation_file'.format(self._var_name())),
        # )
        # for file_path in files:
        #     file = Path(file_path)
        #     if file.is_file() is False:
        #         self.log(message='File {} not found - assuming not yet implemented'.format(file_path), level='info')
        #     else:
        #         self.log(message='File {} found - source files may be manually modified, therefore no checksum comparisons will be done and it is assumed that this file was created previously by the factory'.format(file_path), level='warning')

        variable_cache.store_variable(variable=Variable(name='{}:actions'.format(self._var_name()),initial_value=actions,ttl=-1,logger=self.logger,mask_in_logs=False),overwrite_existing=False)
        if len(actions) > 0:
            return True
        return False

    def _action_create_dir(self, directory_name: str):
        self.log(message='ACTION: Creating directory: {}'.format(directory_name), level='info')
        pass

    def _action_delete_dir_recursively(self, directory_name: str):
        self.log(message='ACTION: Recursively deleting directory: {}'.format(directory_name), level='info')
        pass

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        variable_cache.store_variable(variable=Variable(name='{}:command'.format(self._var_name()),initial_value='apply',ttl=-1,logger=self.logger,mask_in_logs=False),overwrite_existing=False)
        self.log(message='APPLY CALLED', level='info')
        if self.implemented_manifest_differ_from_this_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache) is False:
            self.log(message='No changes detected', level='info')
            return
        actions = variable_cache.get_value(variable_name='{}:actions'.format(self._var_name()), value_if_expired=list(), raise_exception_on_expired=False, raise_exception_on_not_found=False,default_value_if_not_found=list(), for_logging=False)
        self.log(message='actions : {}'.format(actions), level='debug')
        self.log(message='Applying Manifest', level='info')
        self.log(message='   Implementation Name           : {}'.format(self.metadata['name']), level='info')
        for action in actions:
            for action_name, dummy in action.items():
                self.log(message='      action                     : {}'.format(action_name), level='info')


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
        ### Prepare Documentation
        ###

        ###
        ### Prepare Example Manifest
        ###

        ###
        ### Prepare Initial Source File
        ###

        variable_cache.delete_variable(variable_name='{}:command'.format(self._var_name()))
        variable_cache.store_variable(variable=Variable(name='{}'.format(self._var_name()),initial_value=True,ttl=-1,logger=self.logger,mask_in_logs=False),overwrite_existing=False)
        return 
    
    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        variable_cache.store_variable(variable=Variable(name='{}:command'.format(self._var_name()),initial_value='apply',ttl=-1,logger=self.logger,mask_in_logs=False),overwrite_existing=False)
        self.log(message='DELETE CALLED', level='info')
        self.log(message='Deleting Manifest', level='info')
        
        # TODO Delete files

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
        actions = copy.deepcopy(remaining_actions)
        remaining_actions = list()
        
        self._delete_file_path_variables(variable_cache=variable_cache)
        variable_cache.delete_variable(variable_name=self._var_name())
        variable_cache.delete_variable(variable_name='{}:command'.format(self._var_name()))
        return 


if __name__ == '__main__':
    run_main()
