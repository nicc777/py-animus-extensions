from py_animus.manifest_management import *
from py_animus import get_logger
import traceback


class __KIND__(__BASE_CLASS__):
    """__IMPLEMENTATION_DESCRIPTION__
    """    

    def __init__(self, logger=get_logger(), post_parsing_method: object=None, version: str='__VERSION__', supported_versions: tuple=(__SUPPORTED_VERSIONS__)):
        super().__init__(logger=logger, post_parsing_method=post_parsing_method, version=version, supported_versions=supported_versions)

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache())->bool:     
        return False

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        self.log(message='APPLY CALLED', level='info')
        return 
    
    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        self.log(message='DELETE CALLED', level='info')
        return 
