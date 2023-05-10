# WebDownloadFile

Download a file from an Internet URL and save it locally on the filesystem.

The final status will be stored in a `Variable` with `:STATUS` appended to the
variable name. The following values can be expected:

* SUCCESS - Successfully downloaded the file
* FAIL - Some error occurred and the file could not be downloaded

The destination file with ful path will be stored in the `Variable` named `:FILE_PATH`

The remote file will be downloaded under the following conditions:

* The local output file does not exist
* If the local file exist, a HEAD request will be made to the URL and the file sizes will be compared. if the size of the local file is different, the remote file will be downloaded.

```shell
export EXTENSION_NAME="web-download-file-v1"
```

# Spec fields

| Field                                            | Type    | Required | In Versions | Description                                                                                                                                                         |
|--------------------------------------------------|:-------:|:--------:|:-----------:|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `sourceUrl`                                      | string  | Yes      | v1          | The URL from where to download the file                                                                                                                             |
| `targetOutputFile`                               | string  | Yes      | v1          | The destination file. NOTE: The directory MUST exist. To create the directory first (if needed) consider using a ShellScript as a dependency.                       |
| `skipSslVerification`                            | bool    | No       | v1          | If set to true, skips SSL verification. WARNING: use with caution as this may pose a serious security risk                                                          |
| `proxy.host`                                     | string  | No       | v1          | If you need to pass through a proxy, set the proxy host here. Include the protocol and port, for example `http://` or `https://`. An example: `http://myproxy:3128` |
| `proxy.basicAuthentication.username`             | string  | No       | v1          | If the proxy requires authentication and supports basic authentication, set the username here                                                                       |
| `proxy.basicAuthentication.passwordVariableName` | string  | No       | v1          | Contains the `Variable`` name, depending on source manifest implementation, that will contain the password                                                          |
| `extraHeaders`                                   | list    | No       | v1          | A list of name and value items with additional headers to set for the request. Things like a Authorization header might need to be set.                             |
| `method`                                         | string  | No       | v1          | The HTTP method to use (default=GET)                                                                                                                                |
| `body`                                           | string  | No       | v1          | Some request types, like POST, requires a body with the data to send. Also remember to set additional headers like "Content Type" as required                       |
| `httpBasicAuthentication.username`               | string  | No       | v1          | If the remote site requires basic authentication, set the username using this field                                                                                 |
| `httpBasicAuthentication.passwordVariableName`   | string  | No       | v1          | Contains the `Variable`` name, depending on source manifest implementation, that will contain the password                                                          |


# Example Usages

You can run the examples by using the following command after updating your environment variables:

```shell
# Set the examples directory (adjust to suit your needs):
export EXAMPLE_DIR="$PWD/examples"

# Set the appropriate scenario name (see the per scenario examples below)
export SCENARIO_NAME="minimal"

# Run the animus command from a local virtual environment
venv/bin/animus apply -m $EXAMPLE_DIR/$EXTENSION_NAME/$SCENARIO_NAME/example.yaml -s $PWD/implementations
```

## Example: minimal

```shell
export SCENARIO_NAME="minimal"
```

Example manifest: [example.yaml](/media/nicc777/data/nicc777/git/Personal/GitHub/py-animus-extensions/examples/web-download-file-v1/minimal/example.yaml)

```yaml
kind: WebDownloadFile
version: v1
metadata:
  name: web-download-file-v1-minimal
spec:
  sourceUrl: https://raw.githubusercontent.com/nicc777/py-animus-extensions/main/requirements.txt
  targetOutputFile: /tmp/output.html
```

This is the absolute minimal example based on required values. Dummy random data was generated where required.
        

# Versions and Changelog

## Version v1

Initial content for version v1
