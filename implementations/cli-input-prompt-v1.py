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
    * `spec.containsCredentials` - (bool, optional, default=False) - If true, set the for_logging=True parameter for the Variable

    The result will be stored in a variable named `CliInputPrompt:<<metadata.name>>`

    Example Spec

    Test (assuming you are in the root of the cloned repo):

    ```shell
    DEBUG=1 venv/bin/animus apply -m $PWD/examples/cli-input-prompt/basic/get_name.yaml -s $PWD/implementations
    ```

    OR

    ```shell
    docker run --rm -e "DEBUG=0" -it \
        -v $PWD/implementations:/tmp/src \
        -v $PWD/examples/cli-input-prompt/basic:/tmp/data \
        ghcr.io/nicc777/py-animus:latest apply -m /tmp/data/get_name.yaml -s /tmp/src
    ```

    NOTE that the docker example requires the `-it` switch in order to capture user input
    """

    def __init__(self, logger=get_logger(), post_parsing_method: object=None, version: str='v1', supported_versions: tuple=('v1',)):
        super().__init__(logger=logger, post_parsing_method=post_parsing_method, version=version, supported_versions=supported_versions)


    def _var_name(self, target_environment: str='default'):
        return '{}:{}:{}'.format(
            self.__class__.__name__,
            self.metadata['name'],
            target_environment
        )

    def _validate(self, variable_cache: VariableCache=VariableCache(), target_environment: str='default'):
        if self.spec is None:
            self.spec = dict()
        if isinstance(self.spec, dict) is False:
            self.spec = dict()

        if variable_cache.get_value(
            variable_name='{}:validated'.format(self._var_name(target_environment=target_environment)),
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

            if 'containsCredentials' not in self.spec:
                self.spec['containsCredentials'] = False
            else:
                if self.spec['containsCredentials'] is None:
                    self.spec['containsCredentials'] = False
                if isinstance(self.spec['containsCredentials'], bool) is False:
                    self.spec['containsCredentials'] = False

            if 'promptCharacter' not in self.spec:
                self.spec['promptCharacter'] = '> '
            else:
                if self.spec['promptCharacter'] is None:
                    self.spec['promptCharacter'] = '> '
                if isinstance(self.spec['promptCharacter'], str) is False:
                    self.spec['promptCharacter'] = '> '
                if len(self.spec['promptCharacter']) > 64:
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

            if 'maskInput' not in self.spec:
                self.spec['maskInput'] = False
            else:
                if self.spec['maskInput'] is None:
                    self.spec['maskInput'] = False
                if isinstance(self.spec['maskInput'], bool) is False:
                    self.spec['maskInput'] = False

            self.log(message='Spec Validated', level='debug')
        else:
            self.log(message='Already Validated', level='debug')

        variable_cache.store_variable(variable=Variable(name='{}:validated'.format(self._var_name(target_environment=target_environment)),logger=self.logger, initial_value=True), overwrite_existing=True)

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders())->bool:
        if target_environment not in self.metadata['environments']:
            return False
        self._validate(variable_cache=variable_cache)
        current_value = variable_cache.get_value(
            variable_name=self._var_name(target_environment=target_environment),
            value_if_expired=None,
            default_value_if_not_found=None,
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        variable_cache.store_variable(variable=Variable(name='{}:working'.format(self._var_name(target_environment=target_environment)),logger=self.logger, initial_value=current_value))
        if current_value is None:
            return True

        return False

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            return
        self._validate(variable_cache=variable_cache)
        value = None
        self.log(message='variable_cache={}'.format(str(variable_cache)), level='debug')
        if self.implemented_manifest_differ_from_this_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache) is False:
            self.log(message='variable_cache={}'.format(str(variable_cache)), level='debug')
            self.log(message='spec={}'.format(self.spec), level='debug')
            value = variable_cache.get_value(
                variable_name='{}:working'.format(self._var_name(target_environment=target_environment)),
                value_if_expired=None,
                default_value_if_not_found=None,
                raise_exception_on_expired=False,
                raise_exception_on_not_found=False
            )
            self.log(message='value retrieved from CACHE', level='info')
            self.log(message='value retrieved from CACHE value={}'.format(value), level='debug')
            variable_cache.delete_variable(variable_name='{}:working'.format(self._var_name(target_environment=target_environment)))
        else:
            self.log(message='Getting value from USER', level='info')
            self.log(message='variable_cache={}'.format(str(variable_cache)), level='debug')
            self.log(message='spec={}'.format(self.spec), level='debug')
            if self.spec['promptText'] is not None:
                print(self.spec['promptText'])
            if self.spec['maskInput'] is True:
                value = getpass(prompt=self.spec['promptCharacter'])
            else:
                value = input(self.spec['promptCharacter'])
            self.log(message='value={}'.format(value), level='debug')
            if value == '' and self.spec['convertEmptyInputToNone'] is True:
                value = None
            self.log(message='value={}'.format(value), level='debug')

        ttl = -1
        if self.spec['valueExpires'] is True:
            ttl = int(self.spec['valueTTL'])

        variable_cache.store_variable(
            variable=Variable(
                name=self._var_name(target_environment=target_environment),
                initial_value=value,
                ttl=ttl,
                logger=self.logger,
                mask_in_logs=self.spec['containsCredentials']
            ),
            overwrite_existing=True
        )
        self.log(
            message='("{}") Input value "{}"'.format(
                self._var_name(target_environment=target_environment),
                variable_cache.get_value(
                    variable_name=self._var_name(target_environment=target_environment),
                    value_if_expired='',
                    default_value_if_not_found='',
                    raise_exception_on_expired=False,
                    raise_exception_on_not_found=False,
                    for_logging=True
                )
            ),
            level='info'
        )
        return

    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        variable_cache.delete_variable(variable_name=self._var_name(target_environment=target_environment))
        return
