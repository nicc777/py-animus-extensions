
from py_animus.manifest_management import *
from py_animus import get_logger
import traceback
from pathlib import Path
import subprocess
import tempfile
import chardet


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

    def _var_name(self, target_environment: str='default'):
        return '{}:{}:{}'.format(
            self.__class__.__name__,
            self.metadata['name'],
            target_environment
        )

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders())->bool:
        if target_environment not in self.metadata['environments']:
            self.log(message='      Environment Mismatch: Requested environment "{}" but current environments are set to "{}"'.format(target_environment, self.target_environments), level='warning')
            return False
        current_exit_code = variable_cache.get_value(
            variable_name='{}:EXIT_CODE'.format(self._var_name(target_environment=target_environment)),
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

    def _load_source_from_spec(self)->str:
        source = 'exit 0'
        if 'source' in self.spec:
            if 'value' in self.spec['source']:
                source = self.spec['source']['value']
        return source

    def _load_source_from_file(self)->str:
        source = 'exit 0'
        if 'source' in self.spec:
            if 'value' in self.spec['source']:
                try:
                    self.log(message='   Loading script source from file "{}"'.format(self.spec['source']['value']), level='info')
                    with open(self.spec['source']['value'], 'r') as f:
                        source = f.read()
                except:
                    self.log(message='   EXCEPTION: {}'.format(traceback.format_exc()), level='error')
        return source

    def _get_work_dir(self)->str:
        work_dir = tempfile.gettempdir()
        if 'workDir' in self.spec:
            if 'path' in self.spec['workDir']:
                work_dir = self.spec['workDir']['path']
        self.log(message='   Workdir set to "{}"'.format(work_dir), level='info')
        return work_dir

    def _del_file(self, file: str):
        try:
            os.unlink(file)
        except:
            pass

    def _create_work_file(self, source:str)->str:
        work_file = '{}{}{}'.format(
            self._get_work_dir(),
            os.sep,
            self.metadata['name']
        )
        self.log(message='   Writing source code to file "{}"'.format(work_file), level='info')
        self._del_file(file=work_file)
        try:
            with open(work_file, 'w') as f:
                f.write(source)
            self.log(message='      DONE', level='info')
        except:
            self.log(message='   EXCEPTION in _create_work_file(): {}'.format(traceback.format_exc()), level='error')
        return work_file

    def __detect_encoding(self, input_str: str)->str:
        encoding = None
        try:
            encoding = chardet.detect(input_str)['encoding']
        except:
            pass
        return encoding

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            return
        self.log(message='APPLY CALLED', level='info')
        if self.implemented_manifest_differ_from_this_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache, target_environment=target_environment, value_placeholders=value_placeholders) is False:
            self.log(message='   Script already executed', level='info')
            return

        ###
        ### PREP SOURCE FILE
        ###
        script_source = 'exit 0'
        if self._id_source() == 'inline':
            shabang = '#!/bin/sh'
            if 'shellInterpreter' in self.spec:
                shabang = self.spec['shellInterpreter']
                script_source = '#!/usr/bin/env {}\n\n{}'.format(
                    shabang,
                    self._load_source_from_spec()
                )
            else:
                script_source = '{}\n\n{}'.format(
                    shabang,
                    self._load_source_from_spec()
                )
        else:
            script_source = self._load_source_from_file()
        self.log(message='script_source:\n--------------------\n{}\n--------------------'.format(script_source), level='debug')
        work_file = self._create_work_file(source=script_source)

        ###
        ### EXECUTE
        ###
        result = None
        try:
            os.chmod(work_file, 0o700)
            result = subprocess.run('{}'.format(work_file), check=True, capture_output=True)   # Returns CompletedProcess
        except:
            self.log(message='   EXCEPTION in apply_manifest(): {}'.format(traceback.format_exc()), level='error')
            self.log(message='   Storing Variables', level='info')
            try:
                self.log(message='      Storing Exit Code', level='info')
                variable_cache.store_variable(
                    variable=Variable(
                        name='{}:EXIT_CODE'.format(self._var_name(target_environment=target_environment)),
                        initial_value=-999,
                        logger=self.logger
                    ),
                    overwrite_existing=True
                )
                self.log(message='      Storing STDOUT', level='info')
                variable_cache.store_variable(
                    variable=Variable(
                        name='{}:STDOUT'.format(self._var_name(target_environment=target_environment)),
                        initial_value=None,
                        logger=self.logger
                    ),
                    overwrite_existing=True
                )
                self.log(message='      Storing STDERR', level='info')
                variable_cache.store_variable(
                    variable=Variable(
                        name='{}:STDERR'.format(self._var_name(target_environment=target_environment)),
                        initial_value=None,
                        logger=self.logger
                    ),
                    overwrite_existing=True
                )
                self.log(message='      Storing ALL DONE', level='info')
            except:
                self.log(message='   EXCEPTION in apply_manifest() when storing variables: {}'.format(traceback.format_exc()), level='error')

        ###
        ### STORE VALUES
        ###
        if result is not None:
            self.log(message='   Storing Variables', level='info')
            try:
                self.log(message='      Storing Exit Code', level='info')
                value_stdout_encoding = self.__detect_encoding(input_str=result.stdout)
                value_stderr_encoding = self.__detect_encoding(input_str=result.stdout)
                value_stdout_final = result.stdout
                value_stderr_final = result.stderr
                variable_cache.store_variable(
                    variable=Variable(
                        name='{}:EXIT_CODE'.format(self._var_name(target_environment=target_environment)),
                        initial_value=result.returncode,
                        logger=self.logger
                    ),
                    overwrite_existing=True
                )
                self.log(message='      Storing STDOUT', level='info')

                if 'convertOutputToText' in self.spec:
                    if self.spec['convertOutputToText'] is True:
                        if value_stdout_encoding is not None:
                            value_stdout_final = value_stdout_final.decode(value_stdout_encoding)
                        if value_stderr_encoding is not None:
                            value_stderr_final = value_stderr_final.decode(value_stderr_encoding)

                if 'stripNewline' in self.spec:
                    if self.spec['stripNewline'] is True:
                        try:
                            if value_stdout_final is not None:
                                value_stdout_final = value_stdout_final.replace('\n', '')
                                value_stdout_final = value_stdout_final.replace('\r', '')
                            if value_stderr_final is not None:
                                value_stderr_final = value_stderr_final.replace('\n', '')
                                value_stderr_final = value_stderr_final.replace('\r', '')
                        except:
                            traceback.print_exc()
                            self.log(message='Could not remove newline characters after "StripNewline" setting was set to True', level='warning')

                if 'convertRepeatingSpaces' in self.spec:
                    if self.spec['convertRepeatingSpaces'] is True:
                        try:
                            if value_stdout_final is not None:
                                value_stdout_final = ' '.join(value_stdout_final.split())
                            if value_stderr_final is not None:
                                value_stderr_final = ' '.join(value_stderr_final.split())
                        except:
                            traceback.print_exc()
                            self.log(message='Could not remove repeating whitespace characters after "ConvertRepeatingSpaces" setting was set to True', level='warning')

                if 'stripLeadingTrailingSpaces' in self.spec:
                    if self.spec['stripLeadingTrailingSpaces'] is True:
                        try:
                            if value_stdout_final is not None:
                                value_stdout_final = value_stdout_final.strip()
                            if value_stderr_final is not None:
                                value_stderr_final = value_stderr_final.strip()
                        except:
                            traceback.print_exc()
                            self.log(message='Could not remove repeating whitespace characters after "ConvertRepeatingSpaces" setting was set to True', level='warning')

                variable_cache.store_variable(
                    variable=Variable(
                        name='{}:STDOUT'.format(self._var_name(target_environment=target_environment)),
                        initial_value=value_stdout_final,
                        logger=self.logger
                    ),
                    overwrite_existing=True
                )
                self.log(message='      Storing STDERR', level='info')
                variable_cache.store_variable(
                    variable=Variable(
                        name='{}:STDERR'.format(self._var_name(target_environment=target_environment)),
                        initial_value=value_stderr_final,
                        logger=self.logger
                    ),
                    overwrite_existing=True
                )
                self.log(message='      Storing ALL DONE', level='info')
            except:
                self.log(message='   EXCEPTION in apply_manifest() when storing variables: {}'.format(traceback.format_exc()), level='error')
        return_code = variable_cache.get_value(variable_name='{}:EXIT_CODE'.format(self._var_name(target_environment=target_environment)), value_if_expired=None, default_value_if_not_found=None, raise_exception_on_expired=False, raise_exception_on_not_found=False)
        l = 'info'
        if return_code is not None:
            if isinstance(return_code, int):
                if return_code != 0:
                    l = 'error'
        self.log(message='Return Code: {}'.format(return_code), level=l)

        ###
        ### DONE
        ###
        self._del_file(file=work_file)
        return

    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        self.log(message='DELETE CALLED', level='info')
        variable_cache.delete_variable(variable_name='{}:EXIT_CODE'.format(self._var_name(target_environment=target_environment)))
        variable_cache.delete_variable(variable_name='{}:STDOUT'.format(self._var_name(target_environment=target_environment)))
        variable_cache.delete_variable(variable_name='{}:STDERR'.format(self._var_name(target_environment=target_environment)))
        return
