# AwsBoto3CloudFormationTemplate

Creates a new stack or applies a changeset in AWS CloudFormation.

When called with "apply" does one of two actions (default):

1. If the template has not been applied before, apply the new template
2. If the template was applied before, create and apply a change set

The behavior can be fine tuned with the `spec.changeDetection` settings

Variables to be set:

* `FINAL_STATUS` - string with the final CLoudFormation status
* `LOCAL_TEMPLATE_CHECKSUM` - string with the SHA256 checksum of the template in the local file (processed template - not the file checksum)
* `REMOTE_TEMPLATE_CHECKSUM` - string with the SHA256 checksum of the remote template (processed template - not the raw string checksum)
* And any additional mappings as defined in `spec.variableMappings`

The following CloudFormation status codes is assumed to indicate that the stack deployment is complete:

* `CREATE_COMPLETE`
* `CREATE_FAILED`
* `DELETE_COMPLETE`
* `DELETE_FAILED`
* `ROLLBACK_COMPLETE`
* `ROLLBACK_FAILED`
* `UPDATE_COMPLETE`
* `UPDATE_FAILED`
* `UPDATE_ROLLBACK_COMPLETE`
* `UPDATE_ROLLBACK_FAILED`
* `IMPORT_ROLLBACK_FAILED`
* `IMPORT_ROLLBACK_COMPLETE`

References:

* https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html
* https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-describing-stacks.html


```shell
export EXTENSION_NAME="aws_boto3_cloud_formation_template-v1"
```

# Spec fields

| Field                                                    | Type    | Required | In Versions | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|----------------------------------------------------------|:-------:|:--------:|:-----------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `awsBoto3SessionReference`                               | string  | Yes      | v1          | The AWS credentials to use for this template. The value is the "name" of the relevant "AwsBoto3Session" manifest to use                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `tagReferences`                                          | list    | No       | v1          | Reference to the names of a "AwsBoto3CloudFormationTemplateTags" manifests. All tags from these references will be added to the CloudFormation template                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `parameterReferences`                                    | list    | No       | v1          | Reference to the names of  "AwsBoto3CloudFormationTemplateParameters" manifests. All parameters from these references will be added to the CloudFormation template                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `templatePath`                                           | string  | Yes      | v1          | Path to the CloudFormation file. The file must be on the local filesystem or point to a valid S3 URL. If the file is in a Git repository,first use "GitRepo" to get the files onto the local system (as an example)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `options.disableRollback`                                | boolean | No       | v1          | Maps to "DisableRollback" option in the AWS API                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `options.timeoutInMinutes`                               | integer | No       | v1          | Maps to "TimeoutInMinutes" option in the AWS API                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `options.notificationARNs`                               | list    | No       | v1          | Maps to "NotificationARNs" option in the AWS API                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `options.capabilities`                                   | list    | No       | v1          | 'Maps to "Capabilities" option in the AWS API. If supplied, can be "CAPABILITY_IAM" and/or "CAPABILITY_NAMED_IAM"and/or "CAPABILITY_AUTO_EXPAND"'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `options.onFailure`                                      | string  | No       | v1          | Default "ROLLBACK". If supplied, one of "DO_NOTHING" or "ROLLBACK" or "DELETE"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `options.enableTerminationProtection`                    | boolean | No       | v1          | Maps to "EnableTerminationProtection" option in the AWS API                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `changeDetection.features.remoteTemplateValueEvaluation` | boolean | No       | v1          | See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/get_template.html- the remote template will be compared with the current one.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `changeDetection.features.alwaysCreateChangeset`         | boolean | No       | v1          | Regardless if changes are present or not, create a changeset. This makes other change evaluation more or lessredundant.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `changeDetection.customEvaluations.variableEvaluations`  | list    | No       | v1          | Based on the value of a prior set `Variable`, a change can be assumed. Each list item is an object with thefollowing fields: <ul> <li>`variableName` (string) - The name of the "Variable".</li> <li>`expectedValue`(string) - The Python string representation of a variable value.</li> <li>`changeDetectedIfValueMatch`(boolean, default=true) - If the "expectedValue" is matched, assume changes were detected. If "False" and valueOTHER than the "expectedValue" will indicate change was detected.</li> </ul>                                                                                                                                                                                                                               |
| `raiseExceptionOnFinalStatusValues`                      | list    | No       | v1          | Add one or more of the following status codes that will force an exception to be raised (causing further deployment processing to stop). Possible options:<ul>  <li>`CREATE_FAILED` (included in default)</li>  <li>`DELETE_FAILED` (included in default)</li>  <li>`ROLLBACK_FAILED` (included in default)</li>  <li>`UPDATE_FAILED` (included in default)</li>  <li>`UPDATE_ROLLBACK_FAILED` (included in default)</li>  <li>`IMPORT_ROLLBACK_FAILED` (included in default)</li>  <li>`CREATE_COMPLETE`</li>  <li>`DELETE_COMPLETE`</li>  <li>`ROLLBACK_COMPLETE`</li>  <li>`UPDATE_COMPLETE`</li>  <li>`UPDATE_ROLLBACK_COMPLETE`</li>  <li>`IMPORT_COMPLETE`</li>  <li>`IMPORT_ROLLBACK_COMPLETE`</li></ul>An empty list will ignore any status |
| `variableMappings.outputs`                               | list    | No       | v1          | Maps the template outputs to `Variable` objects. Each list item must have the following fields:<ul>  <li>`variableName` (string) - The name of the "Variable", for example `INSTANCE_ID` (the other parts of the name will be automatically added)</li>  <li>`outputKey` (string) - The value of the output key. The same as the CloudFormation output "Logical ID" for example "InstanceID"</li></ul>                                                                                                                                                                                                                                                                                                                                              |
| `variableMappings.resources`                             | list    | No       | v1          | Maps the created resources data to `Variable` objects. Each list item has the following structure:<ul>  <li>`logicalResourceId` (string) - The value of the resource key. The same as the CloudFormation output "Logical ID" for example "InstanceID"</li>  <li>`variables` (list) - Contains a list  of at least ONE item with the following fieldDescription:    <ul>      <li>`physicalResourceId` (string) - `Variable` name for storing the "PhysicalResourceId"</li>      <li>`resourceType` (string) - `Variable` name for storing the "ResourceType"</li>      <li>`resourceStatus` (string) - `Variable` name for storing the "ResourceStatus"</li>    </ul>  </li></ul>                                                                   |

TODO - Add s3 path references

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

Example manifest: [example.yaml](/media/nicc777/data/nicc777/git/Personal/GitHub/py-animus-extensions/examples/aws_boto3_cloud_formation_template-v1/minimal/example.yaml)

```yaml
---
kind: ShellScript
version: v1
metadata:
  name: create-directory
  skipApplyAll: true
  skipDeleteAll: true
spec:
  shellInterpreter: bash
  source:
    type: inLine
    value: mkdir /tmp/cloudformation_templates
---
kind: WriteFile
version: v1
metadata:
  name: my-credentials-sm-cfn-template
  executeOnlyOnceOnApply: true
  dependencies:
    apply:
    - create-directory
  skipApplyAll: true
  skipDeleteAll: true
spec:
  targetFile: /tmp/cloudformation_templates/cfn-example.yaml
  data: |
    AWSTemplateFormatVersion: "2010-09-09"
    Description: 'An example S3 bucket template'
    Parameters:
      UsernameParameter:
        Type: String
    Resources:
      MyCredentials:
        Type: 'AWS::SecretsManager::Secret'
        Properties:
          Name: MyCredentialsForXyz
          Description: "An example secret"
          GenerateSecretString:
            SecretStringTemplate: !Sub
            - '{"username": "${Username}"}'
            - Username: !Ref UsernameParameter
            GenerateStringKey: "password"
            PasswordLength: 40
    Outputs:
      MyCredentialsArn:
        Description: 'ARN for MyCredentials'
        Value: !Ref MyCredentials
        Export:
          Name: !Join [ ":", [ !Ref "AWS::StackName", "MyCredentialsArn" ] ]
      MyCredentialsId:
        Description: 'ID for MyCredentials'
        Value: !GetAtt MyCredentials.Id
        Export:
          Name: !Join [ ":", [ !Ref "AWS::StackName", "MyCredentialsId" ] ]
---
kind: ShellScript
version: v1
metadata:
  name: random-username
  skipApplyAll: true
  skipDeleteAll: true
spec:
  shellInterpreter: bash
  source:
    type: inLine
    value: |
      chars=abcdefghijklmnopqrstuvwxyz1234567890
      for i in {1..16} ; do
      echo -n "${chars:RANDOM%${#chars}:1}"
      done
      echo
  convertOutputToText: true
  stripNewline: true
  convertRepeatingSpaces: true
  stripLeadingTrailingSpaces: true
---
kind: AwsBoto3Session
version: v1
metadata:
  name: aws-boto3-session
  skipApplyAll: true
  skipDeleteAll: true
spec:
  awsRegion: eu-central-1
  profileName: my-profile
---
kind: AwsBoto3Session
version: v1
metadata:
  name: aws-boto3-session-global
  skipApplyAll: true
  skipDeleteAll: true
spec:
  awsRegion: us-east-1
  profileName: my-profile
---
kind: AwsBoto3S3Bucket
version: v1
metadata:
  name: animus-artifacts-for-cloudformation
  dependencies:
    apply:
    - aws-boto3-session-global
    delete:
    - aws-boto3-session-global
  executeOnlyOnceOnApply: true
spec:
  awsBoto3Session:  aws-boto3-session-global
  name: animus-artifacts-for-cloudformation
---
kind: AwsBoto3S3Files
version: v1
metadata:
  name: cfn-upload-to-s3
  dependencies:
    apply:
    - animus-artifacts-for-cloudformation
    - my-credentials-sm-cfn-template
    delete:
    - animus-artifacts-for-cloudformation
  skipApplyAll: true
  skipDeleteAll: true
spec:
  awsBoto3Session: aws-boto3-session-global
  s3Bucket: '{{ .Variables.AwsBoto3S3Bucket:animus-artifacts-for-cloudformation:default:NAME }}'
  globalOverwrite: true
  destinationDirectory: default
  transferLogFile: /tmp/log/file_transfer.log
  sources:
  - sourceType: localFiles
    baseDirectory: /tmp/cloudformation_templates
    files:
    - cfn-example.yaml
  ifFileExists:
    overWrite: true
  onError: warn
  actionExtraFilesOnS3: keep
---
kind: AwsBoto3CloudFormationTemplateParameters
version: v1
metadata:
  name: aws-my-credentials-sm-cfn-template-deployment-parameters
  executeOnlyOnceOnApply: true
  skipApplyAll: true
  skipDeleteAll: true
  apply:
    - random-username
spec:
  parameters:
  - parameterName: 'UsernameParameter'
    parameterValue: '{{ .Variables.ShellScript:random-username:default:STDOUT }}'
---
kind: AwsBoto3CloudFormationTemplateTags
version: v1
metadata:
  name: aws-my-credentials-sm-cfn-template-deployment-tags
  executeOnlyOnceOnApply: true
  skipApplyAll: true
  skipDeleteAll: true
spec:
  tags:
  - tagName: 'Comment'
    tagValue: 'Demonstrating Animus Deployment'
---
kind: AwsBoto3CloudFormationTemplate
version: v1
metadata:
  name: aws-my-credentials-sm-cfn-template-deployment
  dependencies:
    apply:
    - random-username
    - aws-boto3-session
    - aws-my-credentials-sm-cfn-template-deployment-parameters
    - aws-my-credentials-sm-cfn-template-deployment-tags
    - cfn-upload-to-s3
    delete:
    - aws-boto3-session
  executeOnlyOnceOnApply: true
spec:
  awsBoto3SessionReference: aws-boto3-session
  templatePath: 'https://s3.amazonaws.com/{{ .Variables.AwsBoto3S3Bucket:animus-artifacts-for-cloudformation:default:NAME }}/default/cfn-example.yaml'
  parameterReferences:
  - aws-my-credentials-sm-cfn-template-deployment-parameters
  tagReferences:
  - aws-my-credentials-sm-cfn-template-deployment-tags
```

This is the absolute minimal example based on required values. Dummy random data was generated where required.


# Versions and Changelog

## Version v1

Initial content for version v1
