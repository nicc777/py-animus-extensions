from py_animus.manifest_management import *
from py_animus import get_logger
import traceback
import os


DOC_BASE_PATH = '{}{}doc'.format(
    os.getcwd(),
    os.sep
)

EXAMPLES_BASE_PATH = '{}{}examples'.format(
    os.getcwd(),
    os.sep
)

IMPLEMENTATIONS_BASE_PATH = '{}{}examples'.format(
    os.getcwd(),
    os.sep
)



# From https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
class Map(dict): 
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v
        if kwargs:
            for k, v in kwargs.items():
                self[k] = v
    def __getattr__(self, attr):
        return self.get(attr)
    def __setattr__(self, key, value):
        self.__setitem__(key, value)
    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})
    def __delattr__(self, item):
        self.__delitem__(item)
    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


class AnimusExtensionTemplate(ManifestBase):

    def __init__(self, logger=get_logger(), post_parsing_method: object=None, version: str='v1', supported_versions: tuple=('v1',)):
        super().__init__(logger=logger, post_parsing_method=post_parsing_method, version=version, supported_versions=supported_versions)

    def _var_name(self):
        return '{}:{}'.format(
            self.__class__.__name__,
            self.metadata['name']
        )
    
    def _spec_to_map(self, a_dict: dict)->Map:
        d_this = dict()
        if a_dict is not None:
            if isinstance(a_dict, dict):
                for key, val in a_dict.items():
                    if isinstance(val, dict):
                        return Map({key: self._spec_to_map(a_dict=val)})
                    else:
                        d_this[key] = val
                return Map(d_this)
            else:
                return Map()
        return Map()

    def _validate_str(
            self,
            spec_field_dot_notation: str,
            expected_type: type,
            default_val: object,
            set_default_when_not_present: bool=True,        # If false and field is not present, raise exception
            set_default_when_type_mismatch: bool=False,     # By default and exception will be raised
            set_default_when_null: bool=True                # If false and value is None, raise an exception
        )->object:
        spec_path = spec_field_dot_notation.split('.')
        found = False
        value = None
        

        return default_val

    def _validate(self, variable_cache: VariableCache=VariableCache()):
        if self.spec is None:
            self.spec = dict()
        if isinstance(self.spec, dict) is False:
            self.spec = dict()

        spec_map = self._spec_to_map(a_dict=copy.deepcopy(self.spec))

        if variable_cache.get_value(
            variable_name='{}:validated'.format(self._var_name()),
            value_if_expired=False,
            default_value_if_not_found=False,
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        ):
            
            self.log(message='Not Yet Validated', level='debug')

            if 'promptText' not in self.spec:
                self.spec['promptText'] = ''
            else:
                if self.spec['promptText'] is None:
                    self.spec['promptText'] = ''
                if isinstance(self.spec['promptText'], str) is False:
                    self.spec['promptText'] = ''

            

            self.log(message='Spec Validated', level='debug')
        else:
            self.log(message='Already Validated', level='debug')

        variable_cache.store_variable(variable=Variable(name='{}:validated'.format(self._var_name()),logger=self.logger, initial_value=True), overwrite_existing=True)

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache())->bool:

        return False

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):

        return 
    
    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        variable_cache.delete_variable(variable_name=self._var_name())
        return 
