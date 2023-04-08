# Creating Private Extensions

Creating private extensions serves two main purposes:

1. During development of an extension, you can develop in an isolated area without affecting any other public extension repositories
2. Perhaps you really want to keep your extension private because of various reasons, for example proprietary intellectual property used in the implementation

> **Note**
> For point 2, you will probably save your extensions in a private git repository

Using the example from the [main extensions documentation](./create-extensions.md), the example below will create a private extension.

The key directories and files will be as follow:

| Path                                      | Type      | Description                                                                                           |
|-------------------------------------------|-----------|-------------------------------------------------------------------------------------------------------|
| `/tmp/templates/create-text-file-v1.yaml` | File      | The YAML file containing the definition of our extension - a `AnimusExtensionTemplate` manifest, `v1` |
| `/tmp/test-create-text-file-v1/doc`       | Directory | The directory base for our private extension documentation                                            |
| `/tmp/test-create-text-file-v1/impl`      | Directory | The directory for our private extension implementations                                               |
| `/tmp/test-create-text-file-v1/ex`        | Directory | The directory for our examples for private extensions                                                 |
| `/tmp/output`                             | Directory | Where generated output will be saved in files when the extension is tested                            |

Make sure all the directories and files are created:

```shell
mkdir -p /tmp/templates/ && \
  touch /tmp/templates/create-text-file-v1.yaml && \
  mkdir -p /tmp/test-create-text-file-v1/doc && \
  mkdir -p /tmp/test-create-text-file-v1/impl && \
  mkdir -p /tmp/test-create-text-file-v1/ex && \
  mkdir -p /tmp/output

tree /tmp/test-create-text-file-v1
# /tmp/test-create-text-file-v1
# ├── doc
# ├── ex
# └── impl
```

For this example, ensure the file `/tmp/templates/create-text-file-v1.yaml` contains the following content:

```yaml
---
kind: AnimusExtensionTemplate
version: v1
metadata:
  name: create-text-file-v1
  skipDeleteAll: false          # Once the implementation is done, we can set this to `true`
  executeOnlyOnceOnApply: true
  executeOnlyOnceOnDelete: true
spec:
  description: Create/Update a text file with specified content
  kind: CreateTextFile
  version: v1
  versionChangelog: This is the initial version
  supportedVersions:
  - 'v1'
  outputPaths:              # If any of these are null/NoneType, the global defaults will be used (which is this repo)
    doc: '/tmp/test-create-text-file-v1/doc'
    examples: '/tmp/test-create-text-file-v1/ex'
    implementations: '/tmp/test-create-text-file-v1/impl'
  importStatements:
  - 'from py_animus.manifest_management import *'
  - 'from py_animus import get_logger'
  - 'import traceback'
  - 'from pathlib import Path'
  - 'import os'
  - 'import hashlib'
  specFields:
  - fieldName: outputFile
    fieldDescription: The path to the output file that needs to contain the specified content.
    fieldType: str
    fieldRequired: true
    fieldDefaultValue: null
    fieldSetDefaultValueConditions:
    - fieldDefinitionNotPresentInManifest: false
    - fieldValueTypeMismatch: false
    - fieldValueIsNull: false
  - fieldName: content
    fieldDescription: The content of the file as a string. If omitted, an empty file will be created.
    fieldType: str
    fieldRequired: false
    fieldDefaultValue: ''
    fieldSetDefaultValueConditions:
    - fieldDefinitionNotPresentInManifest: true
    - fieldValueTypeMismatch: true
    - fieldValueIsNull: true
  additionalExamples:
  - exampleName: hello-world
    manifest:
      generated: false 
      specData: |
        outputFile: /tmp/output/custom-example-output.txt
        content: |
          Hello Venus
      additionalMetadata: |
        skipDeleteAll: true
    explanatoryText: |
      This is another example that could be used straight out of the box.

      After applying the manifest the output file should contain the text `Hello Venus`. You can test with the following command:

      ```shell
      cat /tmp/output/custom-example-output.txt
      ```
```

As pre-requisite the [py-animus-extensions](https://github.com/nicc777/py-animus-extensions) repository must be cloned. For this example, it is assumed that the current working directory (`$PWD`) is the root of this repository.

It is highly recommended to create a Python virtual environment and install the requirements:

```shell
# Assuming your $PWD is the root of the local clone of the py-animus-extensions github repository 
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
```

Now, the bare-bones extension can be created with the command:

```shell
python3 templates/utils/factory/animus-extension-template.py apply -m /tmp/templates/create-text-file-v1.yaml -s $PWD/templates/utils/factory
```

After running this command, you should now have the following:

```shell
tree /tmp/test-create-text-file-v1 
# /tmp/test-create-text-file-v1
# ├── doc
# │   └── create-text-file-v1.md
# ├── ex
# │   ├── hello-world
# │   │   └── example.yaml
# │   └── minimal
# │       └── example.yaml
# └── impl
#     └── create-text-file-v1.py
```

The skeleton will already work, but it just wont do anything yet:

```shell
docker run --rm -e "DEBUG=0" -it \
  -v /tmp/test-create-text-file-v1/impl:/tmp/src \
  -v /tmp/test-create-text-file-v1/ex/hello-world:/tmp/data \
  -v /tmp/output:/tmp/output \
  ghcr.io/nicc777/py-animus:latest apply -m /tmp/data/example.yaml -s /tmp/src
```

You should see the following log on _**STDOUT**_:

```text
2023-04-08 10:16:23,623 INFO - ok
2023-04-08 10:16:23,626 INFO - Returning CLI Argument Parser
2023-04-08 10:16:23,628 INFO - Registered class kind "CreateTextFile" version "v1" supporting also versions "['v1']" of manifests
2023-04-08 10:16:23,628 INFO - Registered classes: {"CreateTextFile": {"versions": ["v1"]}}
2023-04-08 10:16:23,629 INFO - [CreateTextFile:not-yet-known:v1] Manifest version "v1" found in class supported versions
2023-04-08 10:16:23,629 INFO - ManifestManager:parse_manifest(): NO direct dependency circular reference detected for manifest named "create-text-file-v1-hello-world"
2023-04-08 10:16:23,629 INFO - ManifestManager:parse_manifest(): Stored parsed manifest instance "create-text-file-v1-hello-world:v1:18c74b5df340972e726d4e273a0d2a7245531fbd23448c92dd50d63644044f89"
2023-04-08 10:16:23,629 INFO - Applying manifest named "create-text-file-v1-hello-world:v1:18c74b5df340972e726d4e273a0d2a7245531fbd23448c92dd50d63644044f89"
2023-04-08 10:16:23,629 INFO - [CreateTextFile:create-text-file-v1-hello-world:v1] APPLY CALLED
```

You can now add the method code as described in the [main extensions documentation](./create-extensions.md).

Assuming you are applying the `hello-world` example (file `/tmp/test-create-text-file-v1/ex/hello-world/example.yaml`), the following manifest will be applied:

```yaml
kind: CreateTextFile
version: v1
metadata:
  name: create-text-file-v1-hello-world
  skipDeleteAll: true
spec:
  content: 'Hello Venus

    '
  outputFile: /tmp/output/custom-example-output.txt
```

> **Note**
> The exact file content may differ slightly

The expectation for testing this example therefore is that the text file `/tmp/output/custom-example-output.txt` will be created containing the text `Hello Venus`. To test this, run:

```shell
docker run --rm -e "DEBUG=0" -it \
  -v /tmp/test-create-text-file-v1/impl:/tmp/src \
  -v /tmp/test-create-text-file-v1/ex/hello-world:/tmp/data \
  -v /tmp/output:/tmp/output \
  ghcr.io/nicc777/py-animus:latest apply -m /tmp/data/example.yaml -s /tmp/src
```

Verify:

```shell
ls -lahrt /tmp/output/custom-example-output.txt 
# -rw-r--r-- 1 root root 12 Apr  8 12:26 /tmp/output/custom-example-output.txt

cat /tmp/output/custom-example-output.txt
# Hello Venus
```

> **Note** 
> The file may be owned by `root` depending on your setup with Docker

To test the delete function, run:

```shell
docker run --rm -e "DEBUG=0" -it \
  -v /tmp/test-create-text-file-v1/impl:/tmp/src \
  -v /tmp/test-create-text-file-v1/ex/hello-world:/tmp/data \
  -v /tmp/output:/tmp/output \
  ghcr.io/nicc777/py-animus:latest delete -m /tmp/data/example.yaml -s /tmp/src
```

Note the following log entry:

```text
2023-04-08 10:29:24,395 WARNING - ManifestManager:delete_manifest(): Manifest named "create-text-file-v1-hello-world" skipped because of skipDeleteAll setting
```

Because the default behavior for the `py-animus` command is to run `delete all`, the content in the file was preserved because of the `skipDeleteAll: false` setting in the `/tmp/test-create-text-file-v1/ex/hello-world/example.yaml` manifest.
