
from py_animus.manifest_management import *
from py_animus import get_logger, get_utc_timestamp


class AwsBoto3CloudFormationTemplateTags(ManifestBase):
    """Defines a group of tags that can be linked to one or more CloudFormation templates.

The data will be stored in the following Variable objects:

* `TAG_KEYS` - A list of keys
* `TAGS` - A dictionary in the format { "<<tag_key>>": "<<tag_value>>" }. All tag_value values will be strings

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

        current_tag_keys = variable_cache.get_value(
            variable_name='{}:TAG_KEYS'.format(self._var_name(target_environment=target_environment)),
            value_if_expired=list(),
            default_value_if_not_found=list(),
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        if len(current_tag_keys) == 0:
            return True

        return False

    def _set_variables(self, variable_cache: VariableCache=VariableCache(), target_environment: str='default', input_data: list=list()):
        data = dict()
        self.log(message='input_data={}'.format(input_data), level='debug')
        for tag_pair in input_data:
            self.log(message='   Processing tag_pair={}'.format(tag_pair), level='debug')
            if 'tagName' in tag_pair and 'tagValue' in tag_pair:
                data[tag_pair['tagName']] = '{}'.format(tag_pair['tagValue'])
        self.log(message='data={}'.format(data), level='debug')
        variable_cache.store_variable(
            variable=Variable(
                name='{}:TAG_KEYS'.format(self._var_name(target_environment=target_environment)),
                initial_value=list(data.keys())
            ),
            overwrite_existing=True
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:TAGS'.format(self._var_name(target_environment=target_environment)),
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
            self.log(message='Setting tag variables', level='info')
            self._set_variables(variable_cache=variable_cache, target_environment=target_environment, input_data=self.spec['tags'])
            return

        self.log(message='Nothing to do', level='info')

        return

    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='DELETE CALLED', level='info')
        variable_cache.delete_variable(variable_name='{}:TAG_KEYS'.format(self._var_name(target_environment=target_environment)))
        variable_cache.delete_variable(variable_name='{}:TAGS'.format(self._var_name(target_environment=target_environment)))
        return
