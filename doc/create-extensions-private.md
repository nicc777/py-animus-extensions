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

Make sure all the directories and files are created:

```shell
mkdir -p /tmp/templates/ && \
  touch /tmp/templates/create-text-file-v1.yaml && \
  mkdir -p /tmp/test-create-text-file-v1/doc && \
  mkdir -p /tmp/test-create-text-file-v1/impl && \
  mkdir -p /tmp/test-create-text-file-v1/ex
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
