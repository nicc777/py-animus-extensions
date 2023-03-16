from py_animus.manifest_management import *
from py_animus import get_logger
import traceback
from getpass import getpass


class CliInputPrompt(ManifestBase):
    """Allows to pause for user input

    Spec fields:

    * `spec.promptText` - (str, optional, default=None) The text to display on screen 
    * `spec.promptCharacter` - (str, optional, default='> ') The character for the actual prompt
    * `spec.valueExpires` - (bool, optional, default=False) If set to true, the value will expire after `spec.valueTTL` seconds
    * `spec.valueTTL` - (int, optional, default=60) If `spec.valueExpires` is used, use this value to fine tune the exact timeout period in seconds
    * `spec.convertEmptyInputToNone` - (bool, optional, default=True) - If input is empty, convert the final value to NoneType
    * `spec.maskInput` - (bool, optional, default=False) - If true, do not echo characters. This is suitable to ask for a password, for example

    The result will be stored in a variable named `CliInputPrompt:<<metadata.name>>`

    Example Spec

    NOTE: This does not yet work from DOCKER.

    Test (assuming you are in the root of the cloned repo):

    ```shell
    DEBUG=1 venv/bin/animus apply -m $PWD/examples/cli-input-prompt/basic/get_name.yaml -s $PWD/implementations
    ```
    """

    def __init__(self, logger=get_logger(), post_parsing_method: object=None, version: str='v1', supported_versions: tuple=('v1',)):
        super().__init__(logger=logger, post_parsing_method=post_parsing_method, version=version, supported_versions=supported_versions)
        

    def _var_name(self):
        return '{}:{}'.format(
            self.__class__.__name__,
            self.metadata['name']
        )
    
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
        ):

            if 'promptText' not in self.spec:
                self.spec['promptText'] = ''
            else:
                if self.spec['promptText'] is None:
                    self.spec['promptText'] = ''
                if isinstance(self.spec['promptText'], str) is False:
                    self.spec['promptText'] = ''
            
            if 'promptCharacter' not in self.spec:
                self.spec['promptCharacter'] = '> '
            else:
                if self.spec['promptCharacter'] is None:
                    self.spec['promptCharacter'] = '> '
                if isinstance(self.spec['promptCharacter'], str) is False:
                    self.spec['promptCharacter'] = '> '
                if len(self.spec['promptCharacter']) > 2:
                    self.spec['promptCharacter'] = '> '
            
            if 'valueExpires' not in self.spec:
                self.spec['valueExpires'] = False
            else:
                if self.spec['valueExpires'] is None:
                    self.spec['valueExpires'] = False
                if isinstance(self.spec['valueExpires'], bool) is False:
                    self.spec['valueExpires'] = False

            if self.spec['valueExpires'] is True:
                if 'valueTTL' not in self.spec:
                    self.spec['valueTTL'] = '60'
                else:
                    if self.spec['valueTTL'] is None:
                        self.spec['valueTTL'] = '60'
                    if isinstance(self.spec['valueTTL'], str) is False:
                        self.spec['valueTTL'] = '60'
                    try:
                        int(self.spec['valueTTL'])
                    except:
                        self.spec['valueTTL'] = '60'

            if 'convertEmptyInputToNone' not in self.spec:
                self.spec['convertEmptyInputToNone'] = True
            else:
                if self.spec['convertEmptyInputToNone'] is None:
                    self.spec['convertEmptyInputToNone'] = True
                if isinstance(self.spec['convertEmptyInputToNone'], bool) is False:
                    self.spec['convertEmptyInputToNone'] = True

            print('000')
            if 'maskInput' not in self.spec:
                self.spec['maskInput'] = False
                print('111')
            else:
                if self.spec['maskInput'] is None:
                    print('222')
                    self.spec['maskInput'] = False
                if isinstance(self.spec['maskInput'], bool) is False:
                    print('333')
                    self.spec['maskInput'] = False

        variable_cache.store_variable(variable=Variable(name='{}:validated'.format(self._var_name()),logger=self.logger, initial_value=True), overwrite_existing=True)

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache())->bool:
        self._validate(variable_cache=variable_cache)        
        current_value = variable_cache.get_value(
            variable_name=self._var_name(),
            value_if_expired=None,
            default_value_if_not_found=None,
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        variable_cache.store_variable(variable=Variable(name='{}:working'.format(self._var_name()),logger=self.logger, initial_value=current_value))
        if current_value is None:
            return True
        
        return False

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        self._validate(variable_cache=variable_cache)
        value = None
        value_len = 0
        self.log(message='variable_cache={}'.format(str(variable_cache)), level='debug')
        if self.implemented_manifest_differ_from_this_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache) is False:
            self.log(message='variable_cache={}'.format(str(variable_cache)), level='debug')
            self.log(message='spec={}'.format(self.spec), level='debug')
            value = variable_cache.get_value(
                variable_name='{}:working'.format(self._var_name()),
                value_if_expired=None,
                default_value_if_not_found=None,
                raise_exception_on_expired=False,
                raise_exception_on_not_found=False
            )
            variable_cache.delete_variable(variable_name='{}:working'.format(self._var_name()))
        else:
            self.log(message='variable_cache={}'.format(str(variable_cache)), level='debug')
            self.log(message='spec={}'.format(self.spec), level='debug')
            if self.spec['promptText'] is not None:
                print(self.spec['promptText'])
            if self.spec['maskInput'] is True:
                value = getpass(prompt=self.spec['promptCharacter'])
            else:
                value = input(self.spec['promptCharacter'])
            if value == '' and self.spec['convertEmptyInputToNone'] is True:
                value = None

        ttl = -1
        if self.spec['valueExpires'] is True:
            ttl = int(self.spec['valueTTL'])

        if value is not None:
            value_len = len(value)

        variable_cache.store_variable(
            variable=Variable(
                name=self._var_name(),
                initial_value=value,
                ttl=ttl,
                logger=self.logger
            ),
            overwrite_existing=True
        )
        self.log(message='Captured {} characters from user input and stored in variable named "{}"'.format(value_len, self._var_name()), level='info')
        return 
    
    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        return 
