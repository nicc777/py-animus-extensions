
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

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders())->bool:
        if target_environment not in self.metadata['environments']:
            return False
        
        # Check if the local file exists:
        if os.path.exists(self.spec['targetOutputFile']) is True:
            if Path.is_file(self.spec['targetOutputFile']) is True:
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
        return 
    
    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False, target_environment: str='default', value_placeholders: ValuePlaceHolders=ValuePlaceHolders()):
        if target_environment not in self.metadata['environments']:
            self.log(message='Target environment "{}" not relevant for this manifest'.format(target_environment), level='warning')
            return
        self.log(message='DELETE CALLED', level='info')
        return 
