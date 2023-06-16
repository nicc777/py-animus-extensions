# Features To Implement

| Feature                                                 | Issue           | Description                                                                           |
|---------------------------------------------------------|-----------------|---------------------------------------------------------------------------------------|
| `spec.specFields.customValidation`                      | Not yet created | Include custom validation code in the template when creating the source file skeleton |
| `spec.specFields.fieldSetDefaultValueConditions` fields | Not yet created | Add validation logic                                                                  |
| `spec.pipRequirements` logic                            | Not yet created | Handle specific external Python requirements                                          |


# Upcoming or Planned Extensions

| Name/Kind                                    | Issue                                                                    | Description                                                                                                                                       | Status     |
|----------------------------------------------|--------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|:----------:|
| `CliInputPrompt`                             | n/a                                                                      | Get user input form the command line                                                                                                              | Beta       |
| `ShellScript`                                | [#000001](https://github.com/nicc777/py-animus-extensions/issues/1)      | Run a Shell Script                                                                                                                                | Beta       |
| `WebDownloadFile`                            | [#000008](https://github.com/nicc777/py-animus-extensions/issues/8)      | Download a file from a web source (HTTP or FTP).                                                                                                  | Beta       |
| `GitRepo`                                    | [#000009](https://github.com/nicc777/py-animus-extensions/issues/9)      | Clone a Git Repo                                                                                                                                  | Beta       |
| `AwsBoto3Session`                            | [#000003](https://github.com/nicc777/py-animus-extensions/issues/3)      | Prepare a `boto3` session that can be used in other manifests.                                                                                    | Beta       |
| `AwsBoto3S3Bucket`                           | [#000015](https://github.com/nicc777/py-animus-extensions/issues/15)     | Ensure a S3 bucket exists using `boto3`. Depends usually on `AwsAccount`                                                                          | Beta       |
| `AwsBoto3S3Files`                            | [#000022](https://github.com/nicc777/py-animus-extensions/issues/22)     | Upload file(s) using `boto3`. Depends usually on `AwsBoto3S3Bucket`                                                                               | Beta       |
| `AwsBoto3GetSecret`                          | [#000012](https://github.com/nicc777/py-animus-extensions/issues/12)     | Get the value of a secret in SecretsManager in AWS. Depends usually on `AwsAccount`                                                               | Beta       |
| `WriteFile`                                  | [#000031](https://github.com/nicc777/py-animus-extensions/issues/31)     | Write data to file - typically from a `Value` or a `Variable`                                                                                     | Beta       |
| `GitRepoResource`                            | [#000013](https://github.com/nicc777/py-animus-extensions/issues/13)     | Path to a file or directory in a `GitRepo`                                                                                                        | Planned    |
| `AwsAccount`                                 | [#000005](https://github.com/nicc777/py-animus-extensions/issues/5)      | Prepare a `boto3` session that can be used in other manifests. Depends on `AwsBoto3Session`                                                       | Planned    |
| `AwsBoto3SessionToken`                       | Not yet created                                                          | Retrieves an AWS session token that can be used by other applications. Uses STS `GetSessionToken` API call. Depends usually on `AwsBoto3Session`. | Planned    |
| `AwsBoto3CloudFormationTemplateParameter`    | [#000006](https://github.com/nicc777/py-animus-extensions/issues/6)      | Defines a parameter to be passed into a CloudFormation template                                                                                   | Planned    |
| `AwsBoto3CloudFormationTemplateTag `         | [#000014](https://github.com/nicc777/py-animus-extensions/issues/14)     | Defines a tag to be passed into a CloudFormation template                                                                                         | Planned    |
| `AwsBoto3CloudFormationTemplate`             | [#000004](https://github.com/nicc777/py-animus-extensions/issues/4)      | Deploy/Delete/Update an AWS CloudFormation Template using `boto3`. Depends usually on `AwsAccount` and `AwsBoto3CloudFormationTemplateParameter`  | Planned    |
| `AwsBoto3CreateSecret`                       | Not yet created                                                          | Creates a new SecretsManager secret in AWS. Depends usually on `AwsAccount` and/or `CliInputPrompt`                                               | Planned    |
| `WebUploadFile`                              | Not yet created                                                          | Upload a file to a web server (HTTP or FTP).                                                                                                      | Planned    |
| `Docker*` #1                                 | Not yet created                                                          | [Python Docker](https://docker-py.readthedocs.io/en/stable/) integration to perform various Docker actions. (Depends on `DockerRegistry`)         | Planned    |
| `DockerRegistry`                             | Not yet created                                                          | Defines a Docker registry to use. Must also support login.                                                                                        | Planned    |
| `DockerEcrRegistry`                          | Not yet created                                                          | Defines a AWS ECR registry to use. Must also support login. (Depends on `AwsBoto3Session`)                                                        | Planned    |
| `ScpFile`                                    | Not yet created                                                          | Upload/Download files over SSH (requires `SshCredentials`)                                                                                        | Planned    |
| `AwsEksKubeconfig`                           | Not yet created                                                          | Get the kubectl config for an AWS EKS cluster (depends on `AwsBoto3Session`)                                                                      | Planned    |
| `KubernetesConfig`                           | Not yet created                                                          | Credentials file location for kubectl                                                                                                             | Planned    |
| `K8s*`                                       | Not yet created                                                          | [Python Kubernetes](https://github.com/kubernetes-client/python) integration to interact with Kubernetes. (Depends on `KubernetesConfig`)         | Planned    |
| `NotificationEmailRecipients`                | Not yet created                                                          | Email addresses of people with optional groupings and other configurations                                                                        | Planned    |
| `NotificationSmsRecipients`                  | Not yet created                                                          | Cell numbers of people with optional groupings and other configurations                                                                           | Planned    |
| `NotificationCustomRecipients`               | Not yet created                                                          | Identifiers of recipients or people with optional groupings and other configurations for any REST based messaging end-point                       | Planned    |
| `Notify` #2                                  | Not yet created                                                          | Sends a message. Can use REST methods (depends on `Rest*`) or SMTP (depends on `SmtpClient`) or SNS (depends on `AwsSnsPublish`)                  | Planned    |
| `Rest*`  #3                                  | Not yet created                                                          | [REST Methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)                                                                         | Planned    |
| `SmtpClient`                                 | Not yet created                                                          | Defines a SMTP client that can send messages                                                                                                      | Planned    |
| `AwsSnsPublish`                              | Not yet created                                                          | Publishes a message to an AWS SNS Topic. (Depends on `AwsBoto3Session`)                                                                           | Planned    |
| ~~`SshCredential`~~                          | [#000010](https://github.com/nicc777/py-animus-extensions/issues/10)     | Will no longer be implemented.                                                                                                                    | Scrapped   |
| ~~`HttpBasicCredential`~~                    | [#000011](https://github.com/nicc777/py-animus-extensions/issues/11)     | Will no longer be implemented. See `WebDownloadFile`.                                                                                             | Scrapped   |

Notes:

* #2 - Plan to have a `metadata.notify` field that points to kind `Notify` which in turn can send messages to various messaging end-points. The idea is multiple messaging end-points and audiences are defined in `Notify` depending on events. Recipients are linked via various `Notification*Recipients` kinds.

Planned Docker Kinds (#1):

* `DockerBuild` - For building images
* `DockerPull` - For pulling images from a registry
* `DockerRun` - For running containers
* `DockerPush` - For tagging and pushing images to a registry (may depend on `DockerBuild`)

Kubernetes Kinds (#3):

* `K8sManifest` - Defines the location(s) of manifest file(s)
* `K8sApply` - Deploy a manifest
* `K8sGet` - Get various resources from Kubernetes
* `K8sDelete` - Deletes a manifest

