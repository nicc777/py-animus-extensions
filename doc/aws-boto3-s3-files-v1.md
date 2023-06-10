# AwsBoto3S3Files

Synchronizes files to an S3 bucket (apply action) or deletes the files in an S3 bucket (delete action).

It is important that the bucket remain under control of Animus (both through `AwsBoto3S3Bucket` amd `AwsBoto3S3Files`)
to avoid inconsistencies or loss of dat or data corruption.

The intent of this facility is to keep file synchronized that are required for IaC activities. Ir was not really meant
for uploading or synchronizing a large amount of files. Consider using the AWS CLI tool
[aws s3 sync](https://docs.aws.amazon.com/cli/latest/reference/s3/sync.html) for bulk file uploads (1000+ files)

When the apply action is complete the following variable will be set:

* `:SYNC_RESULT` - Set to the string `ALL_OK`` when done.
* `:CHECKSUM_DIFFERENCES_DETECTED` - Boolean value which will only be present if some files or directories had the `verifyChecksums` parameter set to `true`. If this variable is `true`, it means some of the files evaluated did have a mismatch in checksum and was re-uploaded. If the `verifyChecksums` parameter was never used, this variable may be absent or have a value of `False`

Both individual files, or entire directory contents can be uploaded.

There are several strategies that can be followed:

* Ignore the current files in the bucket, and just overwrite all of them
* A longer process can first get the checksum of each remote file and compare it with the local file and only upload the differences.

Restrictions:

* Please be aware of file and directory (a.k.a. "key") [naming conventions and restriction](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html) for S3.
* Be aware of the AWS S3 [service quotas](https://docs.aws.amazon.com/general/latest/gr/s3.html)
* It is encouraged to re-use the same `AwsBoto3Session` that was used to create the S3 bucket. This will avoid potential issues with end-point usage etc.


```shell
export EXTENSION_NAME="aws-boto3-s3-files-v1"
```

# Spec fields

| Field                     | Type    | Required | In Versions | Description                                                                                                                                                                                                                                                                                                                                                                                                                    |
|---------------------------|:-------:|:--------:|:-----------:|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `awsBoto3Session`         | str     | Yes      | v1          | The name of the `awsBoto3Session`. The appropriate variable name will be derived from this name.                                                                                                                                                                                                                                                                                                                               |
| `s3Bucket`                | str     | Yes      | v1          | The name of the `AwsBoto3S3Bucket` used to manage the S3 bucket. The bucket name will be obtained from this manifest. The bucket name will be in the variable `AwsBoto3S3Bucket:manifest-name:target-environment:NAME` from the `AwsBoto3S3Bucket` manifest                                                                                                                                                                    |
| `destinationDirectory`    | str     | No       | v1          | The destination directory. If not set, the default would be the bucket root (`/`) directory.                                                                                                                                                                                                                                                                                                                                   |
| `localStagingDirectory`   | str     | No       | v1          | Only required if `verifyChecksums` parameter is used. If the `verifyChecksums` parameter is used and this temporary location is not specified, one will be determined programmatically at run time. If the target directory does not exist,an attempt will be made to create it. Post processing, the directory content will be deleted, but the directory will remain.                                                        |
| `sources`                 | list    | Yes      | v1          | A collection (list) of files and/or directories to upload to S3                                                                                                                                                                                                                                                                                                                                                                |
| `ifFileExists.overWrite`  | bool    | Yes      | v1          | If set to `False` (default), any existing files will just be skipped, _**unless**_ the `verifyChecksums` parameter is also used, which will overwrite the file if the checksum mismatches. If set to `True`, the file will be uploaded regardless if it already exists or not and regardless of the `verifyChecksums` parameter.  Therefore, when using the`verifyChecksums` parameter, it is best to keep this value `False`. |
| `onError`                 | str     | Yes      | v1          | The only excepted values is `warn` (just create a warning log entry and carry on) and `exception` which will halt the apply action with an exception.                                                                                                                                                                                                                                                                          |
| `actionExtraFilesOnS3`    | str     | Yes      | v1          | The only excepted values is `keep` (basically ignoring existing files on S3) and `delete` which will remove all files on the S3 bucket not found in the local file map. For consistency, the default is `delete` and it is also the recommended setting for a managed bucket.                                                                                                                                                  |

## Sources

Sources can be defined for local files (`localFiles`) or local directories (`localDirectories`).

Since `spec.sources` expects a list, each list item is a dictionary where the structure depends on the source type (file or directory)

Examples provided assumes the following files:

```text
/path/to/includ/as/base/file1
/path/to/includ/as/base/file2
/path/to/includ/as/base/file3
/path/to/includ/as/base/sub-dir1/file4
/path/to/includ/as/base/sub-dir1/file5
/path/to/includ/as/base/sub-dir1/file6
/path/to/includ/as/base/sub-dir2/file7
/path/to/includ/as/base/sub-dir2/file8
/path/to/includ/as/base/sub-dir2/file9
```

### Local File Dictionary Structure

| Field                     | Type    | Required | In Versions | Description                                                                                                                                                                                                                                                                                                                                                                                                                    |
|---------------------------|:-------:|:--------:|:-----------:|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `sourceType`              | str     | Yes      | v1          | For local files, must be set to `localFiles`. Any other value will cause the list item to be skipped                                                                                                                                                                                                                                                                                                                           |
| `baseDirectory`           | str     | Yes      | v1          | Given the example above, if all 9 files should be included, the base path portion would be `/path/to/includ/as/base`. This portion will not be included in the final S3 key for each file.                                                                                                                                                                                                                                     |
| `verifyChecksums`         | bool    | No       | v1          | Default is `false`. If set to `true`, the corresponding file on S3 (if it exists) will first be downloaded to the `spec.localStagingDirectory` and then the file's checksum will be calculated and compared to the current local file. If the checksum mismatch, the local file will be uploaded to replace the current file in S3.                                                                                            |
| `files`                   | list    | Yes      | v1          | The actual list of files, relative to the `baseDirectory`/ In the example, this would be `file1`, `file2`, `file3`, `sub-dir1/file4`, `sub-dir1/file5`, `sub-dir1/file6` etc.                                                                                                                                                                                                                                                  |

### Local Directory Dictionary Structure

| Field                     | Type    | Required | In Versions | Description                                                                                                                                                                                                                                                                                                                                                                                                                    |
|---------------------------|:-------:|:--------:|:-----------:|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `sourceType`              | str     | Yes      | v1          | For local directories, must be set to `localDirectories`. Any other value will cause the list item to be skipped                                                                                                                                                                                                                                                                                                               |
| `baseDirectory`           | str     | Yes      | v1          | Given the example above, if the two sub-directories should be included, the base path portion would be `/path/to/includ/as/base`. This portion will not be included in the final S3 key for each file.                                                                                                                                                                                                                         |
| `verifyChecksums`         | bool    | No       | v1          | Default is `false`. If set to `true`, the corresponding file on S3 (if it exists) will first be downloaded to the `spec.localStagingDirectory` and then the file's checksum will be calculated and compared to the current local file. If the checksum mismatch, the local file will be uploaded to replace the current file in S3.                                                                                            |
| `recurse`                 | bool    | No       | v1          | Default is `false`. If set to `true`, sub-directories will be dived into relative from the `baseDirectory`. If set to `false`, only the files in the `baseDirectory` and subsequent listed directories will be included.                                                                                                                                                                                                       |
| `directories`             | list    | Yes      | v1          | A list of sub-rectories relative to the `baseDirectory` to scan for files. In the example, if files `file4` to `file9` should be included, the list will include two items: `sub-dir1` and `sub-dir2`                                                                                                                                                                                                                          |


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

Example manifest: [example.yaml](../examples/aws-boto3-s3-files-v1/minimal/example.yaml)

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
---
kind: AwsBoto3S3Files
version: v1
metadata:
  name: aws-s3-files
  dependencies:
    apply:
    - aws-boto3-session-v1-minimal
    - aws-boto3-s3-bucket-v1-minimal # Because we need to ensure the S3 bucket exists first
    delete:
    - aws-boto3-session-v1-minimal # Just delete all the files if the exist on S3 - but we need a session for that...
spec:
  awsBoto3Session: aws-boto3-session-v1-minimal
  s3Bucket: aws-boto3-s3-bucket-v1-minimal # Name of the AwsBoto3S3Bucket manifest to use as reference bucket for the files
  globalOverwrite: false # Optional. If true, no checks will be performed - all files will just be uploaded, regardless of other settings like "ifFileExists" or "verifyChecksums"
  destinationDirectory: /example
  localStagingDirectory: /tmp/staging # If not set, a tmp directory will be calculated and created. Used only when checksums must be verified (this is where the downloaded files go)
  transferLogFile: /tmp/log/file_transfer.log # Optional. Apart from the normal logging, log specific file transfer transactions to this file. If not set, no additional transfer log will be created. If the file exist, new transfers will be appended.
  sources:
  - sourceType: localFiles
    baseDirectory: /tmp/some-dir-1
    verifyChecksums: true # If set to true, very expensive! Downloads each file first to calculate the checksum
    files:
    - file1.txt
    - file2.txt
  - sourceType: localDirectories
    recurse: true
    baseDirectory: /tmp/some-dir-2
    verifyChecksums: false
    directories:
    - sub-dir1/dir1
    - sub-dir2/dir2
  ifFileExists:
    overWrite: true # Overwrite the current version
  onError: warn # Or "exception" to stop further processing
  actionExtraFilesOnS3: keep # or "delete" (default="keep") - what to do with files on S3 not present locally (by matching file path and remote key)
```

This is the absolute minimal example based on required values. Dummy random data was generated where required.


# Versions and Changelog

## Version v1

Initial content for version v1
