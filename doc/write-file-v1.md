# WriteFile

This manifest will take provided data and write it to a file. The file can be (optionally) marked as executable.

The `apply` action will create the file and the `delete` action will delete the file. To retain files on `delete`
action, set the manifest skip option in the meta data.

The following variables will be defined:

* `FILE_PATH` - The full path to the file
* `WRITTEN` - Boolean, where a TRUE value means the file was processed.
* `EXECUTABLE` - Boolean value which will be TRUE if the file has been set as executable
* `SIZE` - The file size in BYTES
* `SHA256_CHECKSUM` - The calculated file checksum (SHA256)


```shell
export EXTENSION_NAME="write-file-v1"
```

# Spec fields

| Field                       | Type    | Required | In Versions | Description                                                                                                                                                               |
|-----------------------------|:-------:|:--------:|:-----------:|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `targetFile`                | str     | Yes      | v1          | Full path to a file                                                                                                                                                       |
| `data`                      | str     | Yes      | v1          | The actual content of the file. Typically a `Value` or `Variable` reference will be used here                                                                             |
| `actionIfFileAlreadyExists` | str     | No       | v1          | optional (default=overwrite). Allowed values: overwrite (write the data to the file anyway - overwriting any previous data), skip (leave the current file as is and skip) |
| `fileMode`                  | str     | No       | v1          | optional (default=normal). Allowed values: normal (chmod 600) or executable (chmod 700)                                                                                   |


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

Example manifest: [example.yaml](examples/write-file-v1/minimal/example.yaml)

```yaml
kind: WriteFile
version: v1
metadata:
  executeOnlyOnceOnApply: true
  name: write-file-v1-minimal
spec:
  data: Hello World!
  targetFile: /tmp/greetings.txt
```

Minimal example creating a text file in the /tmp directory containing a simple greeting.



# Versions and Changelog

## Version v1

Initial content for version v1
