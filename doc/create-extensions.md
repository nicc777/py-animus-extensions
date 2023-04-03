
- [Creating Extensions](#creating-extensions)
- [General Technical Guide](#general-technical-guide)
  - [Introduction](#introduction)
  - [Using py-animus to create the extension template](#using-py-animus-to-create-the-extension-template)
    - [Create an extension template](#create-an-extension-template)
    - [CReate the skeleton extension artifacts](#create-the-skeleton-extension-artifacts)
    - [Update the implementation](#update-the-implementation)
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

TODO - complete...

### Create an extension template

TODO

### CReate the skeleton extension artifacts

TODO

### Update the implementation

TODO

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

