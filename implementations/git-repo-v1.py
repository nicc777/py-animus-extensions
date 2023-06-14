
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

    def _git_clone_from_https(
        self,
        url: str,
        username: str,
        password: str,
        skip_ssl: bool,
        target_dir: str,
        branch: str
    ):
        env = dict()
        if skip_ssl is True:
            env = dict(GIT_SSL_NO_VERIFY='1')
        if username is not None and password is not None:
            url_parts = url.split('/')
            url_parts[2] = '{}:{}@{}'.format(username,password,url_parts[2])
            url = '{}//{}'.format(url_parts[0], '/'.join(url_parts[2:]))
        Repo.clone_from(url=url, to_path=target_dir, env=env, branch=branch)

    def _git_clone_from_ssh(
        self,
        url: str,
        private_key: str,
        target_dir: str,
        branch: str
    ):
        env=dict(GIT_SSH_COMMAND='ssh -i {}'.format(private_key))
        self.log(message='_git_clone_from_ssh(): url         = {}'.format( url         ), level='debug')
        self.log(message='_git_clone_from_ssh(): private_key = {}'.format( private_key ), level='debug')
        self.log(message='_git_clone_from_ssh(): target_dir  = {}'.format( target_dir  ), level='debug')
        self.log(message='_git_clone_from_ssh(): branch      = {}'.format( branch      ), level='debug')
        Repo.clone_from(url=url, to_path=target_dir, env=env, branch=branch)

    def _get_branch(self, variable_cache: VariableCache=VariableCache())->str:
        branch = 'main'
        if 'checkoutBranch' in self.spec:
            if self.spec['checkoutBranch'] is not None:
                branch = '{}'.format(self.spec['checkoutBranch'])
        variable_cache.store_variable(
            variable=Variable(
                name='{}:BRANCH'.format(self._var_name),
                initial_value=branch,
                logger=self.logger
            ),
            overwrite_existing=True
        )
        return branch

    def _process_http_based_git_repo(self, branch: str, variable_cache: VariableCache=VariableCache()):
        username = None
        password = None
        if 'authentication' in self.spec:
            if 'type' in self.spec['authentication']:
                if self.spec['authentication']['type'].lower().startswith('http') is True:
                    try:
                        username = self.spec['authentication']['httpAuthentication']['username']
                        password = self.spec['authentication']['httpAuthentication']['password']
                    except:
                        self.log(message='Failed to set username and password. Continuing with an attempt to clone anonymously.', level='warning')
        self._git_clone_from_https(
            url=self.spec['cloneUrl'].lower(),
            username=username,
            password=password,
            skip_ssl=False,
            target_dir=variable_cache.get_value(
                variable_name='{}:GIT_DIR'.format(self._var_name),
                raise_exception_on_expired=True,
                raise_exception_on_not_found=True
            ),
            branch=branch
        )

    def _process_other_git_repo(self, branch: str, variable_cache: VariableCache=VariableCache()):
        if 'authentication' in self.spec:
            if 'type' in self.spec['authentication']:
                if self.spec['authentication']['type'].lower().startswith('ssh') is True:
                    private_key = None
                    try:
                        private_key = self.spec['authentication']['sshAuthentication']['sshPrivateKeyFile']
                    except:
                        self.log(message='PRIVATE KEY NOT SET - Attempting to clone repository anyway', level='warning')
                    if private_key is not None:
                        self._git_clone_from_ssh(
                            url=self.spec['cloneUrl'].lower(),
                            private_key=private_key,
                            target_dir=variable_cache.get_value(
                                variable_name='{}:GIT_DIR'.format(self._var_name),
                                raise_exception_on_expired=True,
                                raise_exception_on_not_found=True
                            ),
                            branch=branch
                        )
                    else:
                        self.log(message='Failed to clone Git repo - ssh repo without a private key cannot currently be cloned', level='error')
                else:
                    self.log(message='Failed to clone Git repo - Provided authentication type not recognized.', level='error')
            else:
                self.log(message='Failed to clone Git repo - Authentication type required but not present', level='error')
        else:
            self.log(message='Failed to clone Git repo - http not configured and unable to guess protocol and authentication method', level='error')

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
        branch = self._get_branch(variable_cache=variable_cache)
        if self.spec['cloneUrl'].lower().startswith('http') is True:
            self.log(message='Cloning a HTTP repository', level='info')
            self._process_http_based_git_repo(branch=branch, variable_cache=variable_cache)
        else:
            self.log(message='Cloning a SSH repository', level='info')
            self._process_other_git_repo(branch=branch, variable_cache=variable_cache)
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
