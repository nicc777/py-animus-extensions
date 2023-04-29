# AwsBoto3S3Bucket

Manages an S3 bucket. Version aims to support the following features:

* Create a new bucket with the `apply` action
* Delete an existing bucket with the `delete` action that was created earlier with the apply action
    * If the bucket is not empty, the delete behavior will have three options: a) Ignore the delete and just carry on; b) Delete all content, and then delete the bucket; and c) Stop with an error/Exception
* A lot of the supported boto3 options can be set, but in v1 changes to these settings can not yet be handled (planned for a future version). This, for example, applies to changing the ACL or object ownership settings.

Using this manifest depends on `AwsBoto3Session` and will need a dependency for a session manifest.

Since the introduction of environments and variables, it will be possible to use one manifest for buckets in different accounts, assuming at least one AWS account per environment.

The following variables will be set:

* `:BUCKET_EXISTS`: boolean, with a value of `True` if the bucket exists
* `:NAME`: string containing the bucket name


```shell
export EXTENSION_NAME="aws-boto3-s3-bucket-v1"
```

# Spec fields

| Field                        | Type    | Required | In Versions | Description                                                                                                                                                                                                                                                                                     |
|------------------------------|:-------:|:--------:|:-----------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `awsBoto3Session`            | str     | Yes      | v1          | The name of the `awsBoto3Session`. The appropriate variable name will be derived from this name.                                                                                                                                                                                                |
| `name`                       | str     | Yes      | v1          | The name of the AWS bucket. Keep in mind the S3 bucket naming restrictions: https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html                                                                                                                                        |
| `acl`                        | str     | No       | v1          | Corresponds to the Boto3 options `acl` [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html) and [AWS API Documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateBucket.html)                        |
| `grantFullControl`           | str     | No       | v1          | Corresponds to the Boto3 options `grantFullControl` [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html) and [AWS API Documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateBucket.html)           |
| `grantRead`                  | str     | No       | v1          | Corresponds to the Boto3 options `grantRead` [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html) and [AWS API Documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateBucket.html)                  |
| `grantReadACP`               | str     | No       | v1          | Corresponds to the Boto3 options `grantReadACP` [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html) and [AWS API Documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateBucket.html)               |
| `grantWrite`                 | str     | No       | v1          | Corresponds to the Boto3 options `grantWrite` [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html) and [AWS API Documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateBucket.html)                 |
| `grantWriteACP`              | str     | No       | v1          | Corresponds to the Boto3 options `grantWriteACP` [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html) and [AWS API Documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateBucket.html)              |
| `objectLockEnabledForBucket` | boolean | No       | v1          | Corresponds to the Boto3 options `objectLockEnabledForBucket` [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html) and [AWS API Documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateBucket.html) |
| `objectOwnership`            | str     | No       | v1          | Corresponds to the Boto3 options `objectOwnership` [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html) and [AWS API Documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateBucket.html)            |
| `deleteStrategy`             | str     | No       | v1          | Defines the delete strategy which can be one of `IGNORE` (default) or `EMPTY_BUCKET_FIRST` or `ONLY_IF_ALREADY_EMPTY` or `IGNORE_WITH_WARNING_IF_NOT_EMPTY` or `EXCEPTION_IF_NOT_EMPTY`                                                                                                         |

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

Example manifest: [example.yaml](/media/nicc777/data/nicc777/git/Personal/GitHub/py-animus-extensions/examples/aws-boto3-s3-bucket-v1/minimal/example.yaml)

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
kind: AwsBoto3S3Bucket
version: v1
metadata:
  name: aws-boto3-s3-bucket-v1-minimal
  dependencies:
    apply:
    - aws-boto3-session-v1-minimal
    delete:
    - aws-boto3-session-v1-minimal
  executeOnlyOnceOnApply: true
spec:
  awsBoto3Session: aws-boto3-session-v1-minimal
  name: my-very-unique-bucket-name
```

The most basic S3 bucket definition.

> **Note**
> For S3 buckets, the Boto3 session _**must**_ be `us-east-1`

# Versions and Changelog

## Version v1

Initial content for version v1
