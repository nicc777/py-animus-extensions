# AwsBoto3CloudFormationTemplateTags

Defines a group of tags that can be linked to one or more CloudFormation templates.

The data will be stored in the following Variable objects:

* `TAG_KEYS` - A list of keys
* `TAGS` - A dictionary in the format `{ "<<tag_key>>": "<<tag_value>>" }`. All tag_value values will be strings


```shell
export EXTENSION_NAME="aws_boto3_cloud_formation_template_tags-v1"
```

# Spec fields

| Field  | Type    | Required | In Versions | Description  |
|--------|:-------:|:--------:|:-----------:|--------------|
| `tags` | list    | Yes      | v1          | List of tags |


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

Example manifest: [example.yaml](/media/nicc777/data/nicc777/git/Personal/GitHub/py-animus-extensions/examples/aws_boto3_cloud_formation_template_tags-v1/minimal/example.yaml)

```yaml
kind: AwsBoto3CloudFormationTemplateTags
version: v1
metadata:
  executeOnlyOnceOnApply: true
  name: aws_boto3_cloud_formation_template_tags-v1-minimal
spec:
  tags:
  - tagName: 'Owner'
  - tagValue: 'Mickey Mouse'
```

At least one tag must be defined. Each tag object have two keys: `tagName` and `tagValue`. The `tagValue` will
be converted to it's string representation.

# Versions and Changelog

## Version v1

Initial content for version v1
