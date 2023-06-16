
from py_animus.manifest_management import *
from py_animus import get_logger, get_utc_timestamp
from py_animus.file_io import *
import traceback
import os
import stat


class WriteFile(ManifestBase):
    """This manifest will take provided data and write it to a file. The file can be (optionally) marked as executable.

The `apply` action will create the file and the `delete` action will delete the file. To retain files on `delete`
action, set the manifest skip option in the meta data.

The following variables will be defined:

* `FILE_PATH` - The full path to the file
* `WRITTEN` - Boolean, where a TRUE value means the file was processed.
* `EXECUTABLE` - Boolean value which will be TRUE if the file has been set as executable
* `SIZE` - The file size in BYTES
* `SHA256_CHECKSUM` - The calculated file checksum (SHA256)

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

        written_before = variable_cache.get_value(
            variable_name='{}:WRITTEN'.format(self._var_name(target_environment=target_environment)),
            value_if_expired=False,
            default_value_if_not_found=False,
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        file_exists = os.path.exists(self.spec['targetFile'])

        action_if_exists = 'overwrite'
        if 'actionIfFileAlreadyExists' in self.spec:
            if self.spec['actionIfFileAlreadyExists'].lower() in ('overwrite', 'skip',):
                action_if_exists = self.spec['actionIfFileAlreadyExists'].lower()

        if written_before is False:
            if file_exists is True and action_if_exists == 'overwrite':
                return True

        if file_exists is False and written_before is False:
            return True

        return False

    def _set_variables(self, variable_cache: VariableCache=VariableCache(), target_environment: str='default'):
        variable_cache.store_variable(
            variable=Variable(
                name='{}:FILE_PATH'.format(self._var_name(target_environment=target_environment)),
                initial_value=self.spec['targetFile'],
                logger=self.logger,
                mask_in_logs=False
            ),
            overwrite_existing=True
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:WRITTEN'.format(self._var_name(target_environment=target_environment)),
                initial_value=True,
                logger=self.logger,
                mask_in_logs=False
            ),
            overwrite_existing=True
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:EXECUTABLE'.format(self._var_name(target_environment=target_environment)),
                initial_value=os.access(self.spec['targetFile'], os.X_OK),
                logger=self.logger,
                mask_in_logs=False
            ),
            overwrite_existing=True
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:SIZE'.format(self._var_name(target_environment=target_environment)),
                initial_value=get_file_size(file_path=self.spec['targetFile']),
                logger=self.logger,
                mask_in_logs=False
            ),
            overwrite_existing=True
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:SHA256_CHECKSUM'.format(self._var_name(target_environment=target_environment)),
                initial_value=calculate_file_checksum(file_path=self.spec['targetFile'], checksum_algorithm='sha256'),
                logger=self.logger,
                mask_in_logs=False
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
        ) is False:
            self._set_variables(variable_cache=variable_cache, target_environment=target_environment)
            return

        try:
            os.unlink(self.spec['targetFile'])
        except:
            pass
        with open(self.spec['targetFile'], 'w') as f:
            f.write(self.spec['data'])

        if 'fileMode' in self.spec:
            if self.spec['fileMode'].lower().startswith('ex'):
                st = os.stat(self.spec['targetFile'])
                os.chmod(self.spec['targetFile'], st.st_mode | stat.S_IEXEC)

        self._set_variables(variable_cache=variable_cache, target_environment=target_environment)

        return

    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='DELETE CALLED', level='info')

        try:
            os.unlink(self.spec['targetFile'])
        except:
            pass

        variable_cache.delete_variable(variable_name='{}:FILE_PATH'.format(self._var_name(target_environment=target_environment)))
        variable_cache.delete_variable(variable_name='{}:WRITTEN'.format(self._var_name(target_environment=target_environment)))
        variable_cache.delete_variable(variable_name='{}:EXECUTABLE'.format(self._var_name(target_environment=target_environment)))
        variable_cache.delete_variable(variable_name='{}:SIZE'.format(self._var_name(target_environment=target_environment)))
        variable_cache.delete_variable(variable_name='{}:SHA256_CHECKSUM'.format(self._var_name(target_environment=target_environment)))

        return
