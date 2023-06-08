# AwsBoto3GetSecret

Retrieves a secret and stores the value in a variable for use by other manifests

The spec will allow custom Python code to be added for post-secret retrieval processing as may be required for dependent manifests that uses the secret value, for example when only a single value in a complex JSON object is required.

The following variable will be set once the secret is retrieved:

* `VALUE` - contains the secret value
* `TYPE` - Either "string" or "binary"


```shell
export EXTENSION_NAME="aws-boto3-get-secret-v1"
```

# Spec fields

| Field | Type    | Required | In Versions | Description  |
|-------|:-------:|:--------:|:-----------:|--------------|
| `secretName` | str | Yes | v1 | The name of the AWS Secret |
| `awsBoto3SessionReference` | str | Yes | v1 | The AWS credentials to use for this secret. The value is the "name" of the relevant "AwsBoto3Session" manifest to use |
| `conversionTarget` | str | No | v1 | Optional, default=None. Other options: "dict" (assumes the original value is a JSON string) which will convert the secret value to a dict. |


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

Example manifest: [example.yaml](/media/nicc777/data/nicc777/git/Personal/GitHub/py-animus-extensions/examples/aws-boto3-get-secret-v1/minimal/example.yaml)

```yaml
kind: AwsBoto3GetSecret
version: v1
metadata:
  name: aws-boto3-get-secret-v1-minimal
  skipDeleteAll: true
spec:
  awsBoto3SessionReference: my-boto3-session
  secretName: my-secret
```

This is the absolute minimal example based on required values. Dummy random data was generated where required.

## Example: json

```shell
export SCENARIO_NAME="json"
```

Example manifest: [example.yaml](/media/nicc777/data/nicc777/git/Personal/GitHub/py-animus-extensions/examples/aws-boto3-get-secret-v1/json/example.yaml)

```yaml
kind: AwsBoto3GetSecret
version: v1
metadata:
  executeOnlyOnceOnApply: true
  name: aws-boto3-get-secret-v1-json
  skipDeleteAll: true
spec:
  awsBoto3SessionReference: my-boto3-session
  secretName: my-secret
  conversionTarget: dict
```

This example will retrieve the value from the secret and assume it is JSON, which will then be converted into a Python dict.

# Versions and Changelog

## Version v1

Initial content for version v1
