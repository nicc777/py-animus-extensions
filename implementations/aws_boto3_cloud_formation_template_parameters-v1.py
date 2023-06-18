from py_animus.manifest_management import *
from py_animus import get_logger, get_utc_timestamp


class AwsBoto3CloudFormationTemplateParameters(ManifestBase):
    """Defines a list of parameters that can be linked to one or more CloudFormation templates.

The structure of each parameter object:

```yaml
parameterName: string # Required: Will be the"parameter_key"
parameterValue: string
maskParameter: boolean # Optional (default=False). If set to True, the value will be masked in logs. Remember to use "NoEcho" in the actual CloudFormation template to protect sensitive data.
````

The data will be stored in the following Variable objects:

* `PARAMETER_KEYS` - A list of keys
* `PARAMETERS` - A dictionary in the format `{ "<<parameter_key>>": "<<parameter_value>>" }`. All `parameter_value`` values will be strings

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

        current_parameter_keys = variable_cache.get_value(
            variable_name='{}:PARAMETER_KEYS'.format(self._var_name(target_environment=target_environment)),
            value_if_expired=list(),
            default_value_if_not_found=list(),
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        if len(current_parameter_keys) == 0:
            return True

        return False

    def _set_variables(self, variable_cache: VariableCache=VariableCache(), target_environment: str='default', input_data: list=list()):
        data = dict()
        self.log(message='input_data={}'.format(input_data), level='debug')
        for parameter_pair in input_data:
            self.log(message='   Processing parameter_pair={}'.format(parameter_pair), level='debug')
            if 'parameterName' in parameter_pair and 'parameterValue' in parameter_pair:
                data[parameter_pair['parameterName']] = '{}'.format(parameter_pair['parameterValue'])
        self.log(message='data={}'.format(data), level='debug')
        variable_cache.store_variable(
            variable=Variable(
                name='{}:PARAMETER_KEYS'.format(self._var_name(target_environment=target_environment)),
                initial_value=list(data.keys())
            ),
            overwrite_existing=True
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:PARAMETERS'.format(self._var_name(target_environment=target_environment)),
                initial_value=data
            ),
            overwrite_existing=True
        )

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
        ) is True:
            self.log(message='Setting parameter variables', level='info')
            self._set_variables(variable_cache=variable_cache, target_environment=target_environment, input_data=self.spec['parameters'])
            return

        self.log(message='Nothing to do', level='info')

        return

    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='DELETE CALLED', level='info')
        variable_cache.delete_variable(variable_name='{}:PARAMETER_KEYS'.format(self._var_name(target_environment=target_environment)))
        variable_cache.delete_variable(variable_name='{}:PARAMETERS'.format(self._var_name(target_environment=target_environment)))
        return
