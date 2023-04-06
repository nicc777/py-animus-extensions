
- [Creating Extensions](#creating-extensions)
- [General Technical Guide](#general-technical-guide)
  - [Introduction](#introduction)
  - [Using py-animus to create the extension template](#using-py-animus-to-create-the-extension-template)
    - [Create an extension manifest](#create-an-extension-manifest)
    - [Create the skeleton extension artifacts](#create-the-skeleton-extension-artifacts)
    - [Update the implementation](#update-the-implementation)
      - [The `implemented_manifest_differ_from_this_manifest()` method](#the-implemented_manifest_differ_from_this_manifest-method)
      - [The `apply_manifest()` method](#the-apply_manifest-method)
      - [The `delete_manifest()` method](#the-delete_manifest-method)
    - [Test the Implementation](#test-the-implementation)
  - [Making your extension useful](#making-your-extension-useful)
- [Publishing Extensions](#publishing-extensions)


# Creating Extensions

Creating extensions is handled in two parts:

* General technical details on how to proceed with creating extensions
* Publishing options: private vs public, what it means and the processes involved in each

# General Technical Guide

## Introduction

Please read the [README](https://github.com/nicc777/py-animus) of the `py-animus` project to gain a better understanding of what the project is all about. Extensions are used to implement specific "tasks" that react of a specific kind of manifest and at it's core it is an implementation of the `ManifestBase` class from the `py-animus` project.

![py-animus eco system](animus.drawio.png)

The `py-animus` projects main aim is to ensure a certain state is maintained within a certain context. These are deliberately open-ended statements as the system can be used in many different contexts.

The original aim, however, was to create a system that could use different existing implementations of Infrastructure-as-Code across different solution providers and bind them together for the deployment using a single system. This system would need some logic to determine what, if anything, has changed to then run whatever commands or processes is required to achieve a desired state. The source inputs could be a mix between,for example, AWS CloudFormation Templates, Terraform Template and Shell Scripts.

Therefore, this tool does not replace any existing IaC tools, but compliments them by allowing users to use several of these tools in a unified way to deliver one solution.

There are of course more than one way to achieve this goal and even tools like Terraform could potentially be extended to fulfil the same requirement. This is just another option.

An extension is therefore basically a single Python source file which include a class that extends `ManifestBase`. In the examples shown, a very simple example is used where a text string is written to a file. We want to create the file if it does not yet exist and update the content of the file if the content differs from the manifest. We will call this extension `create-text-file` and the manifest kind will be `CreateTextFile`.

The manifest we want will look something like this:

```yaml
---
kind: CreateTextFile
version: v1
metadata:
  name: hello-world
  executeOnlyOnceOnApply: true
  executeOnlyOnceOnDelete: true
spec:
  outputFile: /tmp/hello-world-test.txt
  content: |
    This is a simple multi-line
    test to demonstrate how to
    use py-animus extensions
```

What will happen when we use `py-animus` to _**apply**_ this manifest is the following:

* If the `spec.outputFile` does not exists, create a new file with the content of `spec.content`.
* If the `spec.outputFile` does exists, compare the content of the file with that of `spec.content` and if it is different, update the file with the new content.

What will happen when we use `py-animus` to _**delete**_ this manifest is the following:

* If the `spec.outputFile` does exists, the file will be deleted

## Using py-animus to create the extension template

This repository includes some basic tools to create the necessary files to start the process of creating an extension.

The basic steps to create a new extensions is:

1. Create a template manifest
2. the supplied tool in `templates/utils/factory/animus-extension-template.py` to create the initial extension files: source file, documentation and some example manifests
3. Edit the generated files

### Create an extension manifest

To create extensions, the extension manifest of kind `AnimusExtensionTemplate` must be used.

The extension manifest has the following fields:

| Field                                                                                          | Type    | Required | In Versions  | Description                                                                                                                                                                                                                                                                                                         |
|------------------------------------------------------------------------------------------------|:-------:|:--------:|:------------:|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `kind`                                                                                         | String  | Yes      | `v1`         | Must be `AnimusExtensionTemplate`                                                                                                                                                                                                                                                                                   |
| `version`                                                                                      | String  | Yes      | `v1`         | Currently `v1` is the only option                                                                                                                                                                                                                                                                                   |
| `metadata.name`                                                                                | String  | Yes      | `v1`         | Name of the extension. A good practice is to include the version at the end of the file name, for example `create-text-file-v1`.                                                                                                                                                                                    |
| `metadata.skipApplyAll`                                                                        | Boolean | No       | `v1`         | Probably never used in the context of `AnimusExtensionTemplate`                                                                                                                                                                                                                                                     |
| `metadata.skipDeleteAll`                                                                       | Boolean | No       | `v1`         | Can be set to `true` once the extension skeleton has been created and it must be locked prevent deleting it. Keep value `false` while creating and testing the extension `AnimusExtensionTemplate` file.                                                                                                            |
| `metadata.dependencies.apply`                                                                  | List    | No       | `v1`         | Probably never used in the context of `AnimusExtensionTemplate`                                                                                                                                                                                                                                                     |
| `metadata.dependencies.delete`                                                                 | List    | No       | `v1`         | Probably never used in the context of `AnimusExtensionTemplate`                                                                                                                                                                                                                                                     |
| `metadata.executeOnlyOnceOnApply`                                                              | Boolean | No       | `v1`         | Always set to `true` in the context of `AnimusExtensionTemplate`                                                                                                                                                                                                                                                    |
| `metadata.executeOnlyOnceOnDelete`                                                             | Boolean | No       | `v1`         | Always set to `true` in the context of `AnimusExtensionTemplate`                                                                                                                                                                                                                                                    |
| `spec.<dict>`                                                                                  | Dict    | Yes      | `v1`         | Define the extension attributes in te spec                                                                                                                                                                                                                                                                          |
| `spec.description`                                                                             | String  | No       | `v1`         | If not set or when the value is `null`, will be converted to an empty string. A text description of the extension that will be put in the documentation text as well.                                                                                                                                               |
| `spec.kind`                                                                                    | String  | Yes      | `v1`         | The extension kind. Take care to use a unique kind and try not to re-use names already known/used unless you are creating a new version. Example: `CreateTextFile`                                                                                                                                                  |
| `spec.version`                                                                                 | String  | Yes      | `v1`         | The version of the new extension. Use the convention `v` and then a `<<number>>`, starting with `1` and then increment by `1` with every new version.                                                                                                                                                               |
| `spec.versionChangelog`                                                                        | String  | No       | `v1`         | Used to populate the changelog in the extension documentation.                                                                                                                                                                                                                                                      |
| `spec.supportedVersions`                                                                       | String  | Yes      | `v1`         | Include all the versions compatible with this implementation. By default at least the current version must also be set here. Example: `v1`.                                                                                                                                                                         |
| `spec.baseClass`                                                                               | String  | No       | `v1`         | By default, set to `ManifestBase`. In advanced use-cases other classes can be extended as well.                                                                                                                                                                                                                     |
| `spec.outputPaths`                                                                             | Dict    | No       | `v1`         | Used to override the default file locations for the extension. The default is the locations in this repository.                                                                                                                                                                                                     |
| `spec.outputPaths.doc`                                                                         | String  | No       | `v1`         | Set the output path of the documentation file.                                                                                                                                                                                                                                                                      |
| `spec.outputPaths.examples`                                                                    | String  | No       | `v1`         | Set the output path of the example manifest files.                                                                                                                                                                                                                                                                  |
| `spec.outputPaths.implementations`                                                             | String  | No       | `v1`         | Set the output path of the extension source file.                                                                                                                                                                                                                                                                   |
| `spec.pipRequirements`                                                                         | String  | No       | not-used-yet | Planned for a future version. The intension would be to use additional python packages installed via pip.                                                                                                                                                                                                           |
| `spec.importStatements`                                                                        | String  | No       | `v1`         | ALl the additional imports to add to the top of the extension source file. If not supplied, the following defaults are added: `'from py_animus.manifest_management import *', 'from py_animus import get_logger', 'import traceback',]`                                                                             |
| `spec.specFields`                                                                              | List    | Yes      | `v1`         | The field definitions of the new extension manifest.                                                                                                                                                                                                                                                                |
| `spec.specFields.fieldName`                                                                    | String  | Yes      | `v1`         | The name of the field, for example `outputFile`.                                                                                                                                                                                                                                                                    |
| `spec.specFields.fieldDescription`                                                             | String  | No       | `v1`         | A short description of the field, for example: `The file to which the content will be written`.                                                                                                                                                                                                                     |
| `spec.specFields.fieldType`                                                                    | String  | No       | `v1`         | BY default the type will be `str`. This is only useful as an indicator to a human as to what type of data to use in the field and it is not used in validation (at least at the moment).                                                                                                                            |
| `spec.specFields.fieldRequired`                                                                | Boolean | No       | `v1`         | Default is `false`. Indicates if the field must be set in the manifest or not. If `true`, the field with the default value will be used in the `minimal` example, if auto-generated.                                                                                                                                |
| `spec.specFields.fieldDefaultValue`                                                            | String  | No       | `v1`         | Default is `NoneType` (Python).                                                                                                                                                                                                                                                                                     |
| `spec.specFields.fieldSetDefaultValueConditions`                                               | List    | No       | `v1`         | List of validation conditions. By default all conditions will be set to `true` if none is supplied.                                                                                                                                                                                                                 |
| `spec.specFields.fieldSetDefaultValueConditions.[].fieldDefinitionNotPresentInManifest`        | Boolean | No       | not-used-yet | If false and field is not present, raise exception. NOT CURRENTLY USED. The intention is to inject this into the source file to add the custom field validation functionality when the extension file is created.                                                                                                   |
| `spec.specFields.fieldSetDefaultValueConditions.[].fieldValueTypeMismatch`                     | Boolean | No       | not-used-yet | If `true`, and field type mismatch with `spec.specFields.fieldType` exception will be raised, else the value will be replaced with the default value. NOT CURRENTLY USED. The intention is to inject this into the source file to add the custom field validation functionality when the extension file is created. |
| `spec.specFields.fieldSetDefaultValueConditions.[].fieldValueIsNull`                           | Boolean | No       | not-used-yet | If `false` and value is None, raise an exception, else use the default value. NOT CURRENTLY USED. The intention is to inject this into the source file to add the custom field validation functionality when the extension file is created.                                                                         |
| `spec.specFields.customValidation`                                                             | String  | No       | not-used-yet | Optional Python code for custom field validation. NOT CURRENTLY USED. The intention is to inject this into the source file to add the custom field validation functionality when the extension file is created.                                                                                                     |

Based on the above definition, a basic `AnimusExtensionTemplate` manifest for defining the extension `CreateTextFile` may look like this:

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

```

For using the example, save the file somewhere like `/tmp/templates/create-text-file-v1.yaml`

### Create the skeleton extension artifacts

For this part of the example, the assumption is that the terminal is open in the root directory of this cloned repository.

To create the initial extension files, run the following command:

```shell
python3 templates/utils/factory/animus-extension-template.py \
  apply -m /tmp/templates/create-text-file-v1.yaml \
  -s $PWD/templates/utils/factory
```

After the command is run, the following files would be created:

```shell
tree /tmp/test-create-text-file-v1 
/tmp/test-create-text-file-v1
├── doc
│   └── create-text-file-v1.md
├── ex
│   └── minimal
│       └── example.yaml
└── impl
    └── create-text-file-v1.py

4 directories, 3 files
```

There is a process of refining the manifest in `/tmp/templates/create-text-file-v1.yaml` and each time a refinement needs to be done, go through the following process:

* Run the `apply` command
* Inspect and verify result
* Modify source Manifest
* Run the `delete` command and start again until everything is just right

> **Note**
> AT some point in a future release of [py-animus](https://github.com/nicc777/py-animus) there will also be some kind of version control on the source manifest to detect changes and assist in the decision to apply changes. At the moment this is all still in the hands of the user.

### Update the implementation

The generated source files now needs to be updated.

In this example, the following shows the final code for `/tmp/test-create-text-file-v1/impl/create-text-file-v1.py` generated after the `apply` command:

#### The `implemented_manifest_differ_from_this_manifest()` method

For this example, the change detection logic will go through the following steps:

1. If any of the checks has already been done, just return (no further check required). This is done by checking if any old variables from a previous run exists.
2. Next, check if the file exists. If it does exist, load the content and calculate the checksum.
3. Finally, compare the checksums

```python
class CreateTextFile(ManifestBase):
    
    # Some lines omitted

    def implemented_manifest_differ_from_this_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache())->bool:
        file_content_checksum = None
        new_content_checksum = None
        checksums_mismatch = False

        # If the manifest was already processed, return false
        if  variable_cache.get_value(
            variable_name='{}:executed'.format(self.metadata['name']),
            value_if_expired=False,
            raise_exception_on_expired=False,
            raise_exception_on_not_found=False,
            default_value_if_not_found=False
        ) is True:
            return False

        # For now we assume we are working only with text files - get the checksum for the file content if the file exists
        f = Path(self.spec['outputFile'])
        if f.exists() is True:
            if f.is_file() is True:
                file_hash = hashlib.sha256()
                with open(self.spec['outputFile'], 'r') as of:
                    while chunk := f.read(8192):
                        file_hash.update(chunk.encode('utf-8'))
                file_content_checksum = file_hash.hexdigest()
        else:
            return True

        # Get the checksum of the manifest content and compare to the file checksum
        try:
            content_hash = hashlib.sha256()
            content_hash.update(self.spec['content'].encode('utf-8'))
            new_content_checksum = content_hash.hexdigest()
            if file_content_checksum != new_content_checksum:
                checksums_mismatch = True
        except:
            self.log(message='Failed to determine checksum of new content. EXCEPTION: {}'.format(traceback.format_exc()), level='error')
            variable_cache.store_variable(variable=Variable(name='{}:error'.format(self.metadata['name']),initial_value=True,logger=self.logger),overwrite_existing=True)
            return False

        return checksums_mismatch
```

#### The `apply_manifest()` method

If it is determined by `implemented_manifest_differ_from_this_manifest()` that the file must be created, any potential previous file is first deleted, and then the content is written to the file as defined in the manifest.

```python
class CreateTextFile(ManifestBase):
    
    # Some lines omitted

    def apply_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        self.log(message='APPLY CALLED', level='info')
        variable_cache.store_variable(variable=Variable(name='{}:error'.format(self.metadata['name']),initial_value=False,logger=self.logger),overwrite_existing=True)
        if self.implemented_manifest_differ_from_this_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache) is True:
            # First, remove the current file
            self.delete_manifest(manifest_lookup_function=manifest_lookup_function, variable_cache=variable_cache)

            # Create a new file with the current content
            try:
                with open(self.spec['outputFile'], 'w') as f:
                    f.write(self.spec['content'])
            except:
                self.log(message='Failed to create file "{}". EXCEPTION: {}'.format(self.spec['outputFile'], traceback.format_exc()), level='error')
                variable_cache.store_variable(variable=Variable(name='{}:error'.format(self.metadata['name']),initial_value=True,logger=self.logger),overwrite_existing=True)
        variable_cache.store_variable(variable=Variable(name='{}:executed'.format(self.metadata['name']),initial_value=True,logger=self.logger),overwrite_existing=True)
        return 
```

#### The `delete_manifest()` method

The delete method is fairly straight forward by just deleting the file as specified in the manifest if it already exists

```python
class CreateTextFile(ManifestBase):
    
    # Some lines omitted

    def delete_manifest(self, manifest_lookup_function: object=dummy_manifest_lookup_function, variable_cache: VariableCache=VariableCache(), increment_exec_counter: bool=False):
        self.log(message='DELETE CALLED', level='info')
        variable_cache.store_variable(variable=Variable(name='{}:executed'.format(self.metadata['name']),initial_value=True,logger=self.logger),overwrite_existing=True)
        variable_cache.store_variable(variable=Variable(name='{}:error'.format(self.metadata['name']),initial_value=False,logger=self.logger),overwrite_existing=True)
        try:
            f = Path(self.spec['outputFile'])
            if f.exists() is True:
                if f.is_file() is True:
                    f.unlink(missing_ok=True)
        except:
            self.log(message='Failed to delete file "{}"'.format(self.spec['outputFile']), level='error')
            variable_cache.store_variable(variable=Variable(name='{}:error'.format(self.metadata['name']),initial_value=True,logger=self.logger),overwrite_existing=True)
        return 
```

### Test the Implementation

TODO

## Making your extension useful 

TODO <!-- This will include how to document the extension and prepare examples  -->

# Publishing Extensions

After you have created an extension, you need to decide if/how you are going to publish it.

There are essentially two options:

1. Private, which means you do not opt to make your extension available via the [py-animus-extensions](https://github.com/nicc777/py-animus-extensions) repository (although, you can still host it in your own public repository)
2. Public, which means you want to include your extension in the [py-animus-extensions](https://github.com/nicc777/py-animus-extensions) repository. Your extension will first be reviewed before publishing. 
 

> **Notes**
> The `Public` option is not available yet, as the exact process is still being refined. Please watch this space! 

| Publishing Path Documentation             |
|-------------------------------------------|
| [Private](./create-extensions-private.md) |
| [Public](./create-extensions-public.md)   |

