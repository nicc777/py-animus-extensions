
from py_animus.manifest_management import *
from py_animus import get_logger
from py_animus.file_io import get_file_size
import traceback
from pathlib import Path
import requests


class WebDownloadFile(ManifestBase):
    """Download a file from an Internet URL and save it locally on the filesystem.

The final status will be stored in a `Variable` with `:STATUS` appended to the
variable name. The following values can be expected:

* SUCCESS - Successfully downloaded the file
* FAIL - Some error occurred and the file could not be downloaded

The destination file with ful path will be stored in the `Variable` named `:FILE_PATH`

    """    

    def __init__(self, logger=get_logger(), post_parsing_method: object=None, version: str='v1', supported_versions: tuple=(['v1'])):
        super().__init__(logger=logger, post_parsing_method=post_parsing_method, version=version, supported_versions=supported_versions)

    def _var_name(self, target_environment: str='default'):
        return '{}:{}:{}'.format(
            self.__class__.__name__,
            self.metadata['name'],
            target_environment
        )

    def _get_url_content_length(self, url: str)->dict:
        try:
            response = requests.head(url)
            for header_name, header_value in response.headers.items():
                if header_name.lower() == 'content-length':
                    return int(header_value)
        except:
            self.log(message='EXCEPTION: {}'.format(traceback.format_exc()), level='error')
        raise Exception('Failed to get content length of URL "{}"'.format(url))

    def _set_variables(self, all_ok: bool=True, deleted: bool=False, variable_cache: VariableCache=VariableCache(), target_environment: str='default'):
        result_txt = 'SUCCESS'
        if all_ok is False:
            result_txt = 'FAIL'
        variable_cache.store_variable(
            variable=Variable(
                name='{}:STATUS'.format(self._var_name(target_environment=target_environment)),
                initial_value=result_txt,
                logger=self.logger
            ),
            overwrite_existing=True
        )
        variable_cache.store_variable(
            variable=Variable(
                name='{}:FILE_PATH'.format(self._var_name(target_environment=target_environment)),
                initial_value=self.spec['targetOutputFile'],
                logger=self.logger
            ),
            overwrite_existing=True
        )
        if deleted is True:
            variable_cache.store_variable(
            variable=Variable(
                name='{}:DELETED'.format(self._var_name(target_environment=target_environment)),
                initial_value=True,
                logger=self.logger
            ),
            overwrite_existing=True
        )

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders())->bool:
        if target_environment not in self.metadata['environments']:
            return False
        
        # Check if the local file exists:
        if os.path.exists(self.spec['targetOutputFile']) is True:
            if Path(self.spec['targetOutputFile']).is_file() is True:
                local_file_size = int(get_file_size(file_path=self.spec['targetOutputFile']))
                remote_file_size = self._get_url_content_length(url=self.spec['sourceUrl'])
                self.log(message='local_file_size={}   remote_file_size={}'.format(local_file_size, remote_file_size), level='info')
                if local_file_size != remote_file_size:
                    return True
            else:
                raise Exception('The target output file cannot be used as the named target exists but is not a file')
        else:
            return True

        return False

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='APPLY CALLED', level='info')

        url = self.spec['sourceUrl']
        target_file = self.spec['targetOutputFile']

        if self.implemented_manifest_differ_from_this_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache, target_environment=target_environment, value_placeholders=value_placeholders) is False:
            self._set_variables(all_ok=True, variable_cache=variable_cache, target_environment=target_environment)
            self.log(message='   URL "{}" appears to be already downloaded to target file "{}"'.format(url, target_file), level='info')
            return
        self.log(message='   Downloading URL "{}" to target file "{}"'.format(url, target_file), level='info')

        use_ssl = False
        verify_ssl = True
        use_proxy = False
        use_proxy_authentication = False
        proxy_username = None
        proxy_password = None
        use_http_basic_authentication = False
        http_basic_authentication_username = None
        http_basic_authentication_password = None
        extra_headers = dict()
        http_method = 'GET'
        http_body = None

        if url.lower().startswith('https'):
            use_ssl = True
        if use_ssl is True and 'skipSslVerification' in self.spec:
            verify_ssl = self.spec['skipSslVerification']
        
        if 'proxy' in self.spec:
            if 'host' in self.spec['proxy']:
                use_proxy = True
                if 'basicAuthentication' in self.spec['proxy']:
                    use_proxy_authentication = True
                    proxy_username = self.spec['proxy']['basicAuthentication']['username']
                    proxy_password = variable_cache.get_value(
                        variable_name=self.spec['proxy']['basicAuthentication']['passwordVariableName'],
                        value_if_expired=None,
                        default_value_if_not_found=None,
                        raise_exception_on_expired=False,
                        raise_exception_on_not_found=False
                    )
                    if proxy_password is None:
                        self.log(message='      Proxy Password not Set - Ignoring Proxy AuthenticationConfiguration', level='warning')
                        use_proxy_authentication = False

        if 'httpBasicAuthentication' in self.spec:
            use_http_basic_authentication = True
            http_basic_authentication_username = self.spec['httpBasicAuthentication']['username']
            http_basic_authentication_password = variable_cache.get_value(
                variable_name=self.spec['httpBasicAuthentication']['passwordVariableName'],
                value_if_expired=None,
                default_value_if_not_found=None,
                raise_exception_on_expired=False,
                raise_exception_on_not_found=False
            )
            if http_basic_authentication_password is None:
                self.log(message='      Basic Authentication Password not Set - Ignoring HTTP Basic Authentication Configuration', level='warning')
                use_http_basic_authentication = False

        if 'extraHeaders' in self.spec:
            for header_data in self.spec['extraHeaders']:
                if 'name' in header_data and 'value' in header_data:
                    extra_headers[header_data['name']] = header_data['value']
                else:
                    self.log(message='      Ignoring extra header item as it does not contain the keys "name" and/or "value"', level='warning')

        if 'method' in self.spec:
            http_method = self.spec['method'].upper()
            if http_method not in ('GET','HEAD','POST','PUT','DELETE','PATCH',):
                self.log(message='      HTTP method "{}" not recognized. Defaulting to GET'.format(http_method), level='warning')
                http_method = 'GET'

        if http_method != 'GET' and 'body' in self.spec:
            http_body = self.spec['body']

        self.log(message='   * Using SSL                       : {}'.format(use_ssl), level='info')
        if use_ssl:
            self.log(message='   * Skip SSL Verification SSL       : {}'.format(not verify_ssl), level='info')
        self.log(message='   * Using Proxy                     : {}'.format(use_proxy), level='info')
        if use_proxy:
            self.log(message='   * Using Proxy Authentication      : {}'.format(use_proxy_authentication), level='info')
        self.log(message='   * Using HTTP Basic Authentication : {}'.format(use_http_basic_authentication), level='info')
        if len(extra_headers) > 0:
            self.log(message='   * Extra Header Keys               : {}'.format(list(extra_headers.keys())), level='info')
        else:
            self.log(message='   * Extra Header Keys               : None - Using Default Headers', level='info')
        self.log(message='   * HTTP Method                     : {}'.format(http_method), level='info')
        if http_body is not None:
            self.log(message='   * HTTP Body Bytes                 : {}'.format(len(http_body)), level='info')
        else:
            self.log(message='   * HTTP Body Bytes                 : None', level='info')

        return 
    
    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='DELETE CALLED', level='info')
        if os.path.exists(self.spec['targetOutputFile']) is True:
            if Path(self.spec['targetOutputFile']).is_file() is True:
                try:
                    os.unlink(self.spec['targetOutputFile'])
                    self.log(message='   Deleted target file "{}"'.format(self.spec['targetOutputFile']), level='info')
                except:
                    self.log(message='EXCEPTION: {}'.format(traceback.format_exc()), level='error')
            else:
                self.log(message='   Target file "{}" not deleted as it is not a file'.format(self.spec['targetOutputFile']), level='info')
        else:
            self.log(message='   Target file "{}" already deleted'.format(self.spec['targetOutputFile']), level='info')
        self._set_variables(all_ok=False, deleted=True, variable_cache=variable_cache, target_environment=target_environment)
        return 
