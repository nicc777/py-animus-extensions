
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
        return False

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        self.log(message='APPLY CALLED', level='info')
        return 
    
    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        self.log(message='DELETE CALLED', level='info')
        return 
