# AwsBoto3GetSecret

Retrieves a secret and stores the value in a variable for use by other manifests

The spec will allow custom Python code to be added for post-secret retrieval processing as may be required for dependent manifests that uses the secret value, for example when only a single value in a complex JSON object is required.

The following variable will be set once the secret is retrieved:

* `VALUE` - contains the secret value
* `TYPE` - Either "string" or "binary". If the `conversionTarget` option was used the type may also be "dict"

> **Note**
> When the `delete` action is used, the `apply` action will actually be called. The reasoning is that even in a delete phase, a secret value may be required to perform a delete action on another resource. This manifest is only for reading secrets - not for creating and maintaining the secret.

```shell
export EXTENSION_NAME="aws-boto3-get-secret-v1"
```

# Spec fields

| Field                      | Type    | Required | In Versions | Description                                                                                                                                |
|----------------------------|:-------:|:--------:|:-----------:|--------------------------------------------------------------------------------------------------------------------------------------------|
| `secretName`               | str     | Yes      | v1          | The name of the AWS Secret                                                                                                                 |
| `awsBoto3SessionReference` | str     | Yes      | v1          | The AWS credentials to use for this secret. The value is the "name" of the relevant "AwsBoto3Session" manifest to use                      |
| `conversionTarget`         | str     | No       | v1          | Optional, default=None. Other options: "dict" (assumes the original value is a JSON string) which will convert the secret value to a dict. |


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

Example manifest: [example.yaml](../examples/aws-boto3-get-secret-v1/minimal/example.yaml)

```yaml
---
kind: AwsBoto3Session
version: v1
metadata:
  name: aws-boto3-session-v1-minimal
  skipApplyAll: true
  skipDeleteAll: true
spec:
  awsRegion: us-east-1
  profileName: my-profile
---
kind: AwsBoto3GetSecret
version: v1
metadata:
  name: aws-boto3-get-secret-v1-minimal
  skipDeleteAll: true
  dependencies:
    apply:
    - aws-boto3-session-v1-minimal
    delete:
    - aws-boto3-session-v1-minimal
spec:
  awsBoto3SessionReference: aws-boto3-session-v1-minimal
  secretName: my-secret
```

This is the absolute minimal example based on required values. Dummy random data was generated where required.

## Example: json

```shell
export SCENARIO_NAME="json"
```

Example manifest: [example.yaml](../examples/aws-boto3-get-secret-v1/json/example.yaml)

```yaml
---
kind: AwsBoto3Session
version: v1
metadata:
  name: my-aws-session
  skipApplyAll: true
  skipDeleteAll: true
spec:
  awsRegion: us-east-1
  profileName: my-profile
---
kind: AwsBoto3GetSecret
version: v1
metadata:
  name: my-secret
  skipDeleteAll: true
  dependencies:
    apply:
    - my-aws-session
    delete:
    - my-aws-session
spec:
  awsBoto3SessionReference: my-aws-session
  secretName: DarkSecret
---
kind: ShellScript
version: v1
metadata:
  name: testing-secret-retrieval-and-use
  dependencies:
    apply:
    - my-secret
spec:
  source:
    type: inline
    value: 'echo "Secret: {{ .Variables.AwsBoto3GetSecret:my-secret:default:VALUE }}"'
  convertOutputToText: true
  stripNewline: true
  stripLeadingTrailingSpaces: true
```

This is a good test to show how secrets can be used in practice.

# Versions and Changelog

## Version v1

Initial content for version v1
