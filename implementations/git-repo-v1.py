
from py_animus.manifest_management import *
from py_animus import get_logger, get_utc_timestamp
from py_animus.file_io import *
import traceback
import os
from git import Repo


class GitRepo(ManifestBase):
    """Defines a Git repository.

Running `apply` will clone the Git repository to a local working directory and checkout the default or selected
branch.

If the work directory exists, it will first be deleted in order to clone a fresh copy of the selected repository.

The `delete` action will simply remove the working directory.

The following variables will be set and can be referenced in other manifests using [variable substitution](https://github.com/nicc777/py-animus/blob/main/doc/placeholder_values.md#variables-and-manifest-dependencies)

* `GIT_DIR` - Path to the working directory
* `BRANCH` - The branch checked out

    """

    def __init__(self, logger=get_logger(), post_parsing_method: object=None, version: str='v1', supported_versions: tuple=(['v1'])):
        super().__init__(logger=logger, post_parsing_method=post_parsing_method, version=version, supported_versions=supported_versions)

    def _var_name(self, target_environment: str='default'):
        return '{}:{}:{}'.format(
            self.__class__.__name__,
            self.metadata['name'],
            target_environment
        )

    def _create_temporary_working_directory(self)->str:
        work_dir = ''
        if 'workDir' in self.spec:
            work_dir = self.spec['workDir']
            delete_directory(dir=work_dir)
            create_directory(path=work_dir)
        else:
            work_dir = create_temp_directory()
        return work_dir

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders())->bool:
        if target_environment not in self.metadata['environments']:
            return False
        work_dir = variable_cache.get_value(
            variable_name='{}:GIT_DIR'.format(self._var_name),
            value_if_expired=None,
            default_value_if_not_found=None,
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False
        )
        if work_dir is None:
            work_dir = self._create_temporary_working_directory()
            variable_cache.store_variable(
                variable=Variable(
                    name='{}:GIT_DIR'.format(self._var_name),
                    initial_value=work_dir,
                    logger=self.logger
                ),
                overwrite_existing=True
            )
        return True

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='APPLY CALLED', level='info')
        self.implemented_manifest_differ_from_this_manifest(
            manifest_lookup_function=manifest_lookup_function,
            variable_cache=variable_cache,
            target_environment=target_environment,
            value_placeholders=value_placeholders
        )
        return

    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='DELETE CALLED', level='info')
        self.apply_manifest(
            manifest_lookup_function=manifest_lookup_function,
            variable_cache=variable_cache,
            increment_exec_counter=increment_exec_counter,
            target_environment=target_environment,
            value_placeholders=value_placeholders
        )
        return
