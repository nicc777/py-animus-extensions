
from py_animus.manifest_management import *
from py_animus import get_logger
import traceback
from pathlib import Path
import subprocess


class ShellScript(ManifestBase):
    """Executes a shell script.

Output from STDOUT will be stored in a `Variable` with `:STDOUT` appended to the 
variable name

Output from STDERR will be stored in a `Variable` with `:STDERR` appended to the
variable name

Both STDOUT and STDERR will be stored as strings. No output will result in an
empty sting.

The exit status will be stored in a `Variable` with `:EXIT_CODE` appended to the
variable name

    """    

    def __init__(self, logger=get_logger(), post_parsing_method: object=None, version: str='v1', supported_versions: tuple=(['v1'])):
        super().__init__(logger=logger, post_parsing_method=post_parsing_method, version=version, supported_versions=supported_versions)

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache())->bool:
        current_exit_code = variable_cache.get_value(
            variable_name='{}:EXIT_CODE'.format(self.metadata['name']),
            value_if_expired=None,
            default_value_if_not_found=None,
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        self.log(message='      current_exit_code={}'.format(current_exit_code), level='debug')
        if current_exit_code is not None:
            self.log(message='      returning False', level='debug')
            return False
        self.log(message='      returning True', level='debug')
        return True

    def _id_source(self)->str:
        source = 'inline'
        if 'source' in self.spec:
            if 'type' in self.spec['source']:
                if self.spec['source']['type'] in ('inLine', 'filePath',):
                    source = self.spec['source']['type']
        return source

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        self.log(message='APPLY CALLED', level='info')
        if self.implemented_manifest_differ_from_this_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache) is False:
            self.log(message='   Script already executed', level='info')
            return
        return 
    
    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        self.log(message='DELETE CALLED', level='info')
        variable_cache.delete_variable(variable_name='{}:EXIT_CODE'.format(self.metadata['name']))
        variable_cache.delete_variable(variable_name='{}:STDOUT'.format(self.metadata['name']))
        variable_cache.delete_variable(variable_name='{}:STDERR'.format(self.metadata['name']))
        return 
