# AwsBoto3CloudFormationTemplateParameters

Defines a list of parameters that can be linked to one or more CloudFormation templates.

The data will be stored in the following Variable objects:

* `PARAMETER_KEYS` - A list of keys
* `PARAMETERS` - A dictionary in the format `{ "<<parameter_key>>": "<<parameter_value>>" }`. All `parameter_value` values will be strings

```shell
export EXTENSION_NAME="aws_boto3_cloud_formation_template_parameters-v1"
```

# Spec fields

| Field        | Type    | Required | In Versions | Description        |
|--------------|:-------:|:--------:|:-----------:|--------------------|
| `parameters` | list    | Yes      | v1          | List of parameters |


The structure of each parameter object in the list of `parameters`:

```yaml
parameterName: string # Required: Will be the"parameter_key"
parameterValue: string
maskParameter: boolean # Optional (default=False). If set to True, the value will be masked in logs. Remember to use "NoEcho" in the actual CloudFormation template to protect sensitive data.
```

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

Example manifest: [example.yaml](examples/aws_boto3_cloud_formation_template_parameters-v1/minimal/example.yaml)

```yaml
---
kind: AwsBoto3CloudFormationTemplateParameters
version: v1
metadata:
  executeOnlyOnceOnApply: true
  name: aws_boto3_cloud_formation_template_parameters-v1-minimal
spec:
  parameters:
  - parameterName: 'InstanceAmiParameter'
    parameterValue: '/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2' # See: https://aws.amazon.com/blogs/compute/query-for-the-latest-amazon-linux-ami-ids-using-aws-systems-manager-parameter-store/
```

At least one parameter must be defined. Each parameter object have two keys: `parameterName` and `parameterValue`. The `parameterValue` will
be converted to it's string representation.

# Versions and Changelog

## Version v1

Initial content for version v1
