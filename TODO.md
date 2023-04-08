# Features To Implement

| Feature                                                 | Issue           | Description                                                                           |
|---------------------------------------------------------|-----------------|---------------------------------------------------------------------------------------|
| `spec.specFields.customValidation`                      | Not yet created | Include custom validation code in the template when creating the source file skeleton |
| `spec.specFields.fieldSetDefaultValueConditions` fields | Not yet created | Add validation logic                                                                  |
| `spec.pipRequirements` logic                            | Not yet created | Handle specific external Python requirements                                          |


# Upcoming or Planned Extensions

| Name/Kind                              | Description                                                                                                                                       | Status  |
|----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|:-------:|
| `CliInputPrompt`                       | Get user input form the command line                                                                                                              | DONE    |
| `ShellScript`                          | Run a Shell Script                                                                                                                                | Planned |
| `AwsBoto3Session`                      | Prepare a `boto3` session that can be used in other manifests                                                                                     | Planned |
| `AwsBoto3SessionToken`                 | Retrieves an AWS session token that can be used by other applications. Uses STS `GetSessionToken` API call. Depends usually on `AwsBoto3Session`. | Planned |
| `AwsBoto3CredsProfile`                 | Provides a profile based session via `AwsBoto3Session` using a named profile                                                                      | Planned |
| `AwsBoto3CredsKeys`                    | Provides a profile based session via `AwsBoto3Session` using AWS IAM user keys                                                                    | Planned |
| `AwsBoto3CloudFormationTemplate`       | Deploy/Delete/Update an AWS CloudFormation Template using `boto3`. Depends usually on `AwsBoto3Session`                                           | Planned |
| `WebDownloadFile`                      | Download a file from a web source (HTTP or FTP).                                                                                                  | Planned |
| `WebUploadFile`                        | Upload a file to a web server (HTTP or FTP).                                                                                                      | Planned |
| `DockerRegistry`                       | Defines a Docker registry to use. Must also support login.                                                                                        | Planned |
| `Docker*` #1                           | [Python Docker](https://docker-py.readthedocs.io/en/stable/) integration to perform various Docker actions. (Depends on `DockerRegistry`)         | Planned |
| `DockerEcrRegistry`                    | Defines a AWS ECR registry to use. Must also support login. (Depends on `AwsBoto3Session`)                                                        | Planned |
| `SshCredentials`                       | Use private key or username/password credentials to authenticate to a system over SSH                                                             | Planned |
| `ScpFile`                              | Upload/Download files over SSH (requires `SshCredentials`)                                                                                        | Planned |
| `AwsSecretsManagerGetSecret`           | Allows fetching of secrets stored in AWS Secrets Manager (depends on `AwsBoto3Session`)                                                           | Planned |
| `AwsSecretsManagerCreateSecret`        | Create a new Aws Secret (depends on `AwsBoto3Session`)                                                                                            | Planned |
| `AwsEksKubeconfig`                     | Get the kubectl config for an AWS EKS cluster (depends on `AwsBoto3Session`)                                                                      | Planned |
| `KubernetesConfig`                     | Credentials file location for kubectl                                                                                                             | Planned |
| `K8s*`                                 | [Python Kubernetes](https://github.com/kubernetes-client/python) integration to interact with Kubernetes. (Depends on `KubernetesConfig`)         | Planned |
| `NotificationEmailRecipients`          | Email addresses of people with optional groupings and other configurations                                                                        | Planned |
| `NotificationSmsRecipients`            | Cell numbers of people with optional groupings and other configurations                                                                           | Planned |
| `NotificationCustomRecipients`         | Identifiers of recipients or people with optional groupings and other configurations for any REST based messaging end-point                       | Planned |
| `Notify` #2                            | Sends a message. Can use REST methods (depends on `Rest*`) or SMTP (depends on `SmtpClient`) or SNS (depends on `AwsSnsPublish`)                  | Planned |
| `Rest*`  #3                            | [REST Methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)                                                                         | Planned |
| `SmtpClient`                           | Defines a SMTP client that can send messages                                                                                                      | Planned |
| `AwsSnsPublish`                        | Publishes a message to an AWS SNS Topic. (Depends on `AwsBoto3Session`)                                                                           | Planned |

Notes:

* #2 - Plan to have a `metadata.notify` field that points to kind `Notify` which in turn can send messages to various messaging end-points. The idea is multiple messaging end-points and audiences are defined in `Notify` depeding on events. Recipients are linked via various `Notification*Recipients` kinds.

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

