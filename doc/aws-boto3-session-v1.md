# AwsBoto3Session

Provides a boto3 session object that can be used by other AWS manifests requiring AWS API access via Boto3.

The following variables will be set:

* `:CONNECTED` - A boolean value. If set to `True`, the session object can be used
* `:SESSION` - The Boto3 session object

> **Note**
> The IAM role used for the session must have the following minimum privileges required to set the `:CONNECTED` variable: `sts:GetCallerIdentity`

If the caller identity can be established, the session will be exposed for other services.


# Spec fields

| Field                       | Type    | Required | In Versions | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|-----------------------------|:-------:|:--------:|:-----------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `awsRegion`                 | str     | Yes      | v1          | The region to set                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `profileName`               | str     | No       | v1          | If set, use the named profile for the session authentication.<br><br>See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/session.html for more information.                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `awsAccessKeyId`            | str     | No       | v1          | If set together with `awsSecretAccessKey`, use the supplied credentials. The named profile, if set, will take preference for the session authentication.<br><br>See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/session.html for more information.                                                                                                                                                                                                                                                                                                                                              |
| `awsSecretAccessKey.source` | str     | No       | v1          | Used with awsAccessKeyId<br><br>**Warning**: Use of sensitive information like credentials in manifests is highly discouraged. However, when a secrets store is used to retrieve credentials, these settings can be used. Using profiles is preferred.<br><br>In this implementation, the `source` points to a name of a variable that will contain the secret value. The variable is typically set by another manifest which should be added as a dependency to this manifest when used in this way.<br><br>See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/session.html for more information. |


# Example Usages

You can run the examples by using the following command after updating your environment variables:

```shell
# Set the examples directory (adjust to suit your needs):
export EXAMPLE_DIR="$PWD/examples"

# Run the animus command from a local virtual environment
venv/bin/animus apply -m $EXAMPLE_DIR/aws-boto3-session-v1/$SCENARIO_NAME/example.yaml -s $PWD/implementations -e sandbox
```

## Example: minimal

```shell
export SCENARIO_NAME="minimal"
```

Example manifest: [example.yaml](/media/nicc777/data/nicc777/git/Personal/GitHub/py-animus-extensions/examples/aws-boto3-session-v1/minimal/example.yaml)

```yaml
kind: AwsBoto3Session
metadata:
  executeOnlyOnceOnApply: true
  name: aws-boto3-session-v1-minimal
  skipDeleteAll: true
spec:
  awsRegion: eu-central-1
  profileName: my-profile
version: v1

```

This is the absolute minimal example based on a AWS profile available through the information in `~/.aws` configuration and credential files

        

## Example: aws-session-access-key-sandbox

```shell
export SCENARIO_NAME="aws-session-access-key-sandbox"
```

Example manifest: [example.yaml](/media/nicc777/data/nicc777/git/Personal/GitHub/py-animus-extensions/examples/aws-boto3-session-v1/aws-session-access-key-sandbox/example.yaml)

```yaml
---
kind: ShellScript
metadata:
  name: cli-get-aws-secret-sandbox
  skipDeleteAll: true
  environments:
  - sandbox
spec:
  source:
    type: inline
    value: echo "this-is-a-dummy-secret-key"
version: v1
---
kind: AwsBoto3Session
version: v1
metadata:
  dependencies:
    apply: 
    - cli-get-aws-secret-sandbox
  environments:
  - sandbox
  executeOnlyOnceOnApply: true
  name: aws-boto3-session-v1-aws-session-access-key-sandbox
  skipDeleteAll: true
spec:
  awsAccessKeyId: ABCDEFGHIJKLMNOPQRSTUVWXYZ
  awsRegion: eu-central-1
  awsSecretAccessKey:
    source: '{{ .Variables.ShellScript:cli-get-aws-secret-sandbox:default:STDOUT }}'
```

This example uses AWS access and secret keys to authenticate, and the secret access key is derived from a dependant manifest. This example targets only one specific environment named `sandbox`

        

# Versions and Changelog

## Version v1

Initial content for version v1
