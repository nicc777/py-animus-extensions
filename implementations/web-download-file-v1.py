
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
            response = requests.head(url, allow_redirects=True)
            self.log(message='Headers: {}'.format(response.headers), level='debug')
            for header_name, header_value in response.headers.items():
                if header_name.lower() == 'content-length':
                    self.log(message='Content-Length: {}'.format(int(header_value)), level='info')
                    return int(header_value)
        except:
            self.log(message='EXCEPTION: {}'.format(traceback.format_exc()), level='error')
        # It may be impossible to get the initial length as we did not take into account proxy or authentication. In these cases assume a LARGE file
        return 999999999999

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
        
        remote_file_size = self._get_url_content_length(url=self.spec['sourceUrl'])
        variable_cache.store_variable(
            variable=Variable(
                name='{}:CONTENT_LENGTH'.format(self._var_name(target_environment=target_environment)),
                initial_value=remote_file_size,
                logger=self.logger
            ),
            overwrite_existing=True
        )

        # Check if the local file exists:
        if os.path.exists(self.spec['targetOutputFile']) is True:
            if Path(self.spec['targetOutputFile']).is_file() is True:
                local_file_size = int(get_file_size(file_path=self.spec['targetOutputFile']))
                self.log(message='local_file_size={}   remote_file_size={}'.format(local_file_size, remote_file_size), level='info')
                if local_file_size != remote_file_size:
                    return True
            else:
                raise Exception('The target output file cannot be used as the named target exists but is not a file')
        else:
            return True

        return False

    def _build_proxy_dict(self, proxy_host: str, proxy_username: str, proxy_password: str)->dict:
        proxies = dict()
        proxy_str = ''
        if proxy_host is not None:
            if isinstance(proxy_host, str):
                if proxy_host.startswith('http'):
                    proxy_str = proxy_host
                    if proxy_username is not None and proxy_password is not None:
                        if isinstance(proxy_username, str) and isinstance(proxy_password, str):
                            creds = '//{}:{}@'.format(proxy_username, proxy_password)
                            creds_logging = '//{}:{}@'.format(proxy_username, '*' * len(proxy_password))
                            final_proxy_str = '{}{}{}'.format(proxy_str.split('/')[0], creds, '/'.join(proxy_str.split('/')[2:]))
                            final_proxy_str_logging = '{}{}{}'.format(proxy_str.split('/')[0], creds_logging, '/'.join(proxy_str.split('/')[2:]))
                            self.log(message='Using proxy "{}"'.format(final_proxy_str_logging), level='info')
                            proxies['http'] = final_proxy_str
                            proxies['https'] = final_proxy_str
        return proxies

    def _get_data_basic_request(
        self, 
        url: str,
        target_file: str,
        verify_ssl: bool,
        proxy_host: str,
        proxy_username: str,
        proxy_password: str,
        username: str,
        password: str,
        headers: dict,
        method: str,
        body: str
    )->bool:
        self.log(message='Running Method "_get_data_basic_request"', level='debug')
        try:
            proxies=self._build_proxy_dict(proxy_host=proxy_host, proxy_username=proxy_username, proxy_password=proxy_password)
            r = requests.get(url=url, allow_redirects=True, verify=verify_ssl, proxies=proxies)
            with open(target_file, 'wb') as f:
                f.write(r.content)
        except:
            self.log(message='EXCEPTION: {}'.format(traceback.format_exc()), level='error')
            return False
        return True

    def _get_data_basic_request_stream(
        self, 
        url: str,
        target_file: str,
        verify_ssl: bool,
        proxy_host: str,
        proxy_username: str,
        proxy_password: str,
        username: str,
        password: str,
        headers: dict,
        method: str,
        body: str
    )->bool:
        # Refer to https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
        self.log(message='Running Method "_get_data_basic_request_stream"', level='debug')
        try:
            proxies=self._build_proxy_dict(proxy_host=proxy_host, proxy_username=proxy_username, proxy_password=proxy_password)
            with requests.get(url, stream=True, allow_redirects=True, verify=verify_ssl, proxies=proxies) as r:
                r.raise_for_status()
                with open(target_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        f.write(chunk)
        except:
            self.log(message='EXCEPTION: {}'.format(traceback.format_exc()), level='error')
            return False
        return True

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

        remote_file_size = variable_cache.get_value(variable_name='{}:CONTENT_LENGTH'.format(self._var_name(target_environment=target_environment)), raise_exception_on_expired=True, raise_exception_on_not_found=True)
        large_file = False
        self.log(message='Checking if {} > 104857600...'.format(remote_file_size), level='info')
        if remote_file_size > 104857600:   # Anything larger than 100MiB is considered large and will be downloaded in chunks
            large_file = True 

        use_ssl = False
        verify_ssl = True
        use_proxy = False
        use_proxy_authentication = False
        proxy_host = None
        proxy_username = None
        proxy_password = None
        use_http_basic_authentication = False
        http_basic_authentication_username = None
        http_basic_authentication_password = None
        extra_headers = dict()
        use_custom_headers = False
        http_method = 'GET'
        http_body = None
        use_body = False

        if url.lower().startswith('https'):
            use_ssl = True
        if use_ssl is True and 'skipSslVerification' in self.spec:
            verify_ssl = not self.spec['skipSslVerification']
        
        if 'proxy' in self.spec:
            if 'host' in self.spec['proxy']:
                use_proxy = True
                proxy_host = self.spec['proxy']['host']
                if 'basicAuthentication' in self.spec['proxy']:
                    use_proxy_authentication = True
                    proxy_username = self.spec['proxy']['basicAuthentication']['username']
                    proxy_password = variable_cache.get_value(
                        variable_name=self.spec['proxy']['basicAuthentication']['passwordVariableName'],
                        value_if_expired=None,
                        default_value_if_not_found=None,
                        raise_exception_on_expired=False,
                        raise_exception_on_not_found=False
                    ).strip()
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
            ).strip()
            if http_basic_authentication_password is None:
                self.log(message='      Basic Authentication Password not Set - Ignoring HTTP Basic Authentication Configuration', level='warning')
                use_http_basic_authentication = False

        if 'extraHeaders' in self.spec:
            for header_data in self.spec['extraHeaders']:
                if 'name' in header_data and 'value' in header_data:
                    extra_headers[header_data['name']] = header_data['value']
                else:
                    self.log(message='      Ignoring extra header item as it does not contain the keys "name" and/or "value"', level='warning')
        if len(extra_headers) > 0:
            use_custom_headers = True

        if 'method' in self.spec:
            http_method = self.spec['method'].upper()
            if http_method not in ('GET','HEAD','POST','PUT','DELETE','PATCH',):
                self.log(message='      HTTP method "{}" not recognized. Defaulting to GET'.format(http_method), level='warning')
                http_method = 'GET'

        if http_method != 'GET' and 'body' in self.spec:
            http_body = self.spec['body']
        if http_body is not None:
            if len(http_body) > 0:
                use_body = True

        self.log(message='   * Large File                      : {}'.format(large_file), level='info')
        self.log(message='   * Using SSL                       : {}'.format(use_ssl), level='info')
        if use_ssl:
            self.log(message='   * Skip SSL Verification           : {}'.format(not verify_ssl), level='info')
        self.log(message='   * Using Proxy                     : {}'.format(use_proxy), level='info')
        if use_proxy:
            self.log(message='   * Proxy Host                      : {}'.format(proxy_host), level='info')
            self.log(message='   * Using Proxy Authentication      : {}'.format(use_proxy_authentication), level='info')
            if use_proxy_authentication is True:
                self.log(message='   * Proxy Password Length           : {}'.format(len(proxy_password)), level='info')
        self.log(message='   * Using HTTP Basic Authentication : {}'.format(use_http_basic_authentication), level='info')
        if use_http_basic_authentication:
            self.log(message='   * HTTP Password Length            : {}'.format(len(http_basic_authentication_password)), level='info')
        if len(extra_headers) > 0:
            self.log(message='   * Extra Header Keys               : {}'.format(list(extra_headers.keys())), level='info')
        else:
            self.log(message='   * Extra Header Keys               : None - Using Default Headers', level='info')
        self.log(message='   * HTTP Method                     : {}'.format(http_method), level='info')
        if http_body is not None:
            self.log(message='   * HTTP Body Bytes                 : {}'.format(len(http_body)), level='info')
        else:
            self.log(message='   * HTTP Body Bytes                 : None', level='info')

        work_values = {
            'large_file': large_file,
            'verify_ssl': verify_ssl,
            'use_proxy': use_proxy,
            'use_proxy_authentication': use_proxy_authentication,
            'use_http_basic_authentication': use_http_basic_authentication,
            'http_method': http_method,
            'use_custom_headers': use_custom_headers,
            'use_body': use_body,
        }

        parameters = {
            'url': url,
            'target_file': target_file,
            'verify_ssl': verify_ssl,
            'proxy_host': proxy_host,
            'proxy_username': proxy_username,
            'proxy_password': proxy_password,
            'username': http_basic_authentication_username,
            'password': http_basic_authentication_password,
            'headers': extra_headers,
            'method': http_method,
            'body': http_body
        }
        download_scenarios = [
            {
                'values': {
                    'large_file': False,
                    'use_http_basic_authentication': False,
                    'http_method': ('GET', ),
                    'use_custom_headers': False,
                    'use_body': False,
                },
                'method': self._get_data_basic_request
            },
            {
                'values': {
                    'large_file': True,
                    'use_http_basic_authentication': False,
                    'http_method': ('GET', ),
                    'use_custom_headers': False,
                    'use_body': False,
                },
                'method': self._get_data_basic_request_stream
            },
        ]

        effective_method = None
        for scenario in download_scenarios:
            values = scenario['values']
            criterion_match = True
            for criterion, condition in values.items():
                if criterion != 'http_method':
                    if condition != work_values[criterion]:
                        criterion_match = False
                else:
                    if work_values['http_method'] not in condition:
                        criterion_match = False
            if criterion_match is True:
                effective_method = scenario['method']

        if effective_method is not None:
            result = effective_method(**parameters)
            if result is True:
                self._set_variables(all_ok=True, deleted=False, variable_cache=variable_cache, target_environment=target_environment)
            else:
                raise Exception('Failed to download "{}" to file "{}"'.format(url, target_file))
        else:
            raise Exception('No suitable method could be found to handle the download.')
            
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
