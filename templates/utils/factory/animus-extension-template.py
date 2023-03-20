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
            raise_exception_when_empty: bool=False
        )->object:
        final_value = default_val
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
        self.log(message='Spec path "{}" validated'.format(spec_path), level='info')
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
                            raise_exception_when_empty=params['raise_exception_when_empty']
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
        variable_cache.store_variable(
            variable=Variable(
                name='{}:example_dir'.format(self._var_name()),
                initial_value='{}{}minimal'.format(EXAMPLES_BASE_PATH, os.sep),
                ttl=-1,
                logger=self.logger,
                mask_in_logs=False
            ),
            overwrite_existing=False
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:example_file'.format(self._var_name()),
                initial_value='{}{}minimal{}{}.yaml'.format(EXAMPLES_BASE_PATH, os.sep, os.sep, self.metadata['name']),
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
        files = (
            Path(variable_cache.get_value(variable_name='{}:doc_file'.format(self._var_name()))),
            Path(variable_cache.get_value(variable_name='{}:example_file'.format(self._var_name()))),
            Path(variable_cache.get_value(variable_name='{}:implementation_file'.format(self._var_name()))),
        )
        for file in files:
            if file.is_file() is False:
                self.log(message='File {} not found - assuming not yet implemented'.format(file.name), level='info')
                return True
        return False

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        self.log(message='APPLY CALLED', level='info')
        if self.implemented_manifest_differ_from_this_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache) is False:
            self.log(message='No changes detected', level='info')
            return
        self.log(message='Applying Manifest', level='info')
        self.log(message='   Implementation Name           : {}'.format(self.metadata['name']), level='info')
        self.log(message='      Documentation File         : {}'.format(variable_cache.get_value(variable_name='{}:doc_file'.format(self._var_name()))), level='info')
        self.log(message='      Minimal Example File       : {}'.format(variable_cache.get_value(variable_name='{}:example_file'.format(self._var_name()))), level='info')
        self.log(message='      Implementation Source File : {}'.format(variable_cache.get_value(variable_name='{}:implementation_file'.format(self._var_name()))), level='info')
        return 
    
    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        self.log(message='DELETE CALLED', level='info')
        self.log(message='Deleting Manifest', level='info')
        
        # TODO Delete files
        
        self._delete_file_path_variables(variable_cache=variable_cache)
        variable_cache.delete_variable(variable_name=self._var_name())
        return 


if __name__ == '__main__':
    run_main()
