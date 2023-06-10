# ShellScript

Executes a shell script.

Output from STDOUT will be stored in a `Variable` with `:STDOUT` appended to the
variable name

Output from STDERR will be stored in a `Variable` with `:STDERR` appended to the
variable name

Both STDOUT and STDERR will be stored as strings. No output will result in an
empty sting.

The exit status will be stored in a `Variable` with `:EXIT_CODE` appended to the
variable name


```shell
export EXTENSION_NAME="shell-script-v1"
```

# Spec fields

| Field                        | Type     | Required | In Versions | Description                                                                                                                                                                                                                                     |
| ---------------------------- | :------: | :------: | :---------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `shellInterpreter`           |  str     |    No    |     v1      | The shell interpreter to select in the shabang line. Supported values: `sh`, `zsh`, `perl`, `python` and `bash`                                                                                                                                 |
| `source`                     |  dict    |    Yes   |     v1      | Defines the script source                                                                                                                                                                                                                       |
| `source.type`                |  str     |    No    |     v1      | Select the source type, which can be either `filePath` that points to an existing script file on the local file system, or `inLine` with the script source defined in the `spec.source.value` field                                             |
| `source.value`               |  str     |    No    |     v1      | If `spec.source.type` has a value of `inLine` then the value here will be assumed to be the script content of that type. if `spec.source.type` has a value of `filePath` then this value must point to an existing file on the local filesystem |
| `workDir.path`               |  str     |    No    |     v1      | An optional path to a working directory. The extension will create temporary files (if needed) in this directory and execute them from here.                                                                                                    |
| `convertOutputToText`        |  bool    |    No    |     v1      | Normally the STDOUT and STDERR will be binary encoded. Setting this value to true will convert those values to a normal string. Default=False                                                                                                   |
| `stripNewline`               |  bool    |    No    |     v1      | Output may include newline or other line break characters. Setting this value to true will remove newline characters. Default=False                                                                                                             |
| `convertRepeatingSpaces`     |  bool    |    No    |     v1      | Output may contain more than one repeating space or tab characters. Setting this value to true will replace these with a single space. Default=False                                                                                            |
| `stripLeadingTrailingSpaces` |  bool    |    No    |     v1      | Output may contain more than one repeating space or tab characters. Setting this value to true will replace these with a single space. Default=False                                                                                            |


# Example Usages

You can run the examples by using the following command after updating your environment variables:

```shell
# Set the examples directory (adjust to suit your needs):
export EXAMPLE_DIR="$PWD/examples"

# If you need to create an output file, also set and mount the output path (adjust to suit your needs):
mkdir /tmp/output
export OUTPUT_PATH=/tmp/output

docker run --rm -e "DEBUG=1" -it \
  -v $PWD/implementations:/tmp/src \
  -v $EXAMPLE_DIR/$EXTENSION_NAME/$SCENARIO_NAME:/tmp/data \
  -v $OUTPUT_PATH:/tmp/output \
  ghcr.io/nicc777/py-animus:latest apply -m /tmp/data/example.yaml -s /tmp/src
```



## Example: minimal

```shell
export SCENARIO_NAME="minimal"
```

Example manifest: [example.yaml](../examples/shell-script-v1/minimal/example.yaml)

```yaml
kind: ShellScript
metadata:
  name: shell-script-v1-minimal
  skipDeleteAll: true
spec:
  source:
    type: inline
    value: echo "not yet fully implemented"
version: v1

```

This is the absolute minimal example based on required values. Dummy random data was generated where required.



## Example: docker-check

```shell
export SCENARIO_NAME="docker-check"
```

Example manifest: [example.yaml](../examples/shell-script-v1/docker-check/example.yaml)

```yaml
kind: ShellScript
metadata:
  name: shell-script-v1-docker-check
  skipDeleteAll: true
spec:
  shellInterpreter: bash
  source:
    value: 'docker --version

      '
version: v1

```

This example runs the command `docker --version` and will store the result in the variable named



# Versions and Changelog

## Version v1

Initial content for version v1
