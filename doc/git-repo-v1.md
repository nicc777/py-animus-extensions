# GitRepo

Defines a Git repository.

Running `apply` will clone the Git repository to a local working directory and checkout the default or selected
branch.

If the work directory exists, it will first be deleted in order to clone a fresh copy of the selected repository.

The `delete` action will simply remove the working directory.

The following variables will be set and can be referenced in other manifests using [variable substitution](https://github.com/nicc777/py-animus/blob/main/doc/placeholder_values.md#variables-and-manifest-dependencies)

* `GIT_DIR` - Path to the working directory
* `BRANCH` - The branch checked out

> **Note**
> The `apply` action will also be called on an explicit `delete` action. If the Git repository is not required for any
> other delete actions, it is safe to add the `skipDeleteAll` option in the meta data section of the manifest.

```shell
export EXTENSION_NAME="git-repo-v1"
```

# Spec fields

| Field                                                | Type    | Required | In Versions | Description                                                                                                                                                                                                                                                                                                                            |
|------------------------------------------------------|:-------:|:--------:|:-----------:|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `cloneUrl`                                           | str     | Yes      | v1          | The URL to the GIt repository to clone locally into the working directory                                                                                                                                                                                                                                                              |
| `authentication.type`                                | str     | No       | v1          | Must be either "http" or "ssh". If not supplied, no authentication will be used and the repository will be assumed to be public.                                                                                                                                                                                                       |
| `authentication.httpAuthentication.username`         | str     | No       | v1          | The username for HTTP(S) based Git repositories. Only required if `authentication.type` is set to `http`                                                                                                                                                                                                                               |
| `authentication.httpAuthentication.password`         | str     | No       | v1          | The password for HTTP(S) based Git repositories. Only required if `authentication.type` is set to `http`. Never put the actual password. See https://github.com/nicc777/py-animus/blob/main/doc/placeholder_values.md and https://github.com/nicc777/py-animus/blob/main/doc/placeholder_values.md#variables-and-manifest-dependencies |
| `authentication.sshAuthentication.sshPrivateKeyFile` | str     | No       | v1          | The full path to the SSH private key. Only required if `authentication.type` is set to `ssh`. For SSH this is for now the only supported option.                                                                                                                                                                                       |
| `workDir`                                            | str     | No       | v1          | If supplied, this directory will be used to clone the Git repository into. If not supplied, a random temporary directory will be created. The final value will be in the `GIT_DIR` variable.                                                                                                                                           |
| `checkoutBranch`                                     | str     | No       | v1          | If supplied, this branch will be checked out. Default=main                                                                                                                                                                                                                                                                             |
| `options.skipSslVerify`                              | bool    | No       | v1          | If `authentication.type` is `http` and there is a need to skip SSL verification, set this to `true`. Default=false                                                                                                                                                                                                                     |


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

Example manifest: [example.yaml](/media/nicc777/data/nicc777/git/Personal/GitHub/py-animus-extensions/examples/git-repo-v1/minimal/example.yaml)

```yaml
kind: GitRepo
version: v1
metadata:
  executeOnlyOnceOnApply: true
  name: git-repo-v1-minimal
  skipDeleteAll: true
spec:
  cloneUrl: https://github.com/aws-cloudformation/aws-cloudformation-samples.git
```

Minimal example cloning a public repository

## Example: http-with-authentication-self-signed-certificate

```shell
export SCENARIO_NAME="http-with-authentication-self-signed-certificate"
```

Example manifest: [example.yaml](/media/nicc777/data/nicc777/git/Personal/GitHub/py-animus-extensions/examples/git-repo-v1/http-with-authentication-self-signed-certificate/example.yaml)

```yaml
---
kind: AwsBoto3Session
version: v1
metadata:
  name: my-boto3-session
  skipApplyAll: true
  skipDeleteAll: true
spec:
  awsRegion: us-east-1
  profileName: my-profile
---
kind: AwsBoto3GetSecret
version: v1
metadata:
  name: my-private-git-password
  skipDeleteAll: true
  dependencies:
    apply:
    - my-boto3-session
spec:
  awsBoto3SessionReference: my-boto3-session
  secretName: my-secret
---
kind: GitRepo
version: v1
metadata:
  name: git-repo-v1-http-with-authentication-self-signed-certificate
  executeOnlyOnceOnApply: true
  skipDeleteAll: true
  dependencies:
    apply:
    - my-private-git-password
spec:
  authentication:
    type: http
    httpAuthentication:
      username: my-username
      password: '{{ .Variables.AwsBoto3GetSecret:my-private-git-password:default:VALUE }}'
  checkoutBranch: feature/abc
  cloneUrl: https://private-git/example.git
  options:
    skipSslVerify: true
```

This example shows a local HTTPS based repository that requires authentication, but with the option to skip SSL verification (_**Warning**_: this approach is not secure)

## Example: ssh-repository

```shell
export SCENARIO_NAME="ssh-repository"
```

Example manifest: [example.yaml](/media/nicc777/data/nicc777/git/Personal/GitHub/py-animus-extensions/examples/git-repo-v1/ssh-repository/example.yaml)

```yaml
---
kind: GitRepo
version: v1
metadata:
  executeOnlyOnceOnApply: true
  name: git-repo-v1-ssh-repository
  skipDeleteAll: true
spec:
  authentication:
    type: ssh
    sshAuthentication:
      sshPrivateKeyFile: /path/to/ssh-privatekey
  checkoutBranch: feature/abc
  cloneUrl: git@github.com:my-org/my-private-repo.git
```

Demonstrates cloning of a typical private repository on Github using SSH


# Versions and Changelog

## Version v1

Initial content for version v1
