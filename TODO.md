# Upcoming or Planned Extensions

| Name/Kind                              | Description                                                                                                 | Status  |
|----------------------------------------|-------------------------------------------------------------------------------------------------------------|:-------:|
| `CliInputPrompt`                       | Get user input form the command line                                                                        | DONE    |
| `ShellScript`                          | Run a Shell Script                                                                                          | Planned |
| `AwsBoto3Session`                      | Prepare a `boto3` session that can be used in other manifests                                               | Planned |
| `AwsSessionToken`                      | Retrieves an AWS session token that can be used by other applications. Uses STS `GetSessionToken` API call. | Planned |
| `AwsBoto3CredsProfile`                 | Provides a profile based session via `AwsBoto3Session` using a named profile                                | Planned |
| `AwsBoto3CredsKeys`                    | Provides a profile based session via `AwsBoto3Session` using AWS IAM user keys                              | Planned |
| `AwsBoto3DeployCloudFormationTemplate` | Deploy an AWS CloudFormation Template using `boto3`. Depends usually on  `AwsBoto3Session`                  | Planned |
