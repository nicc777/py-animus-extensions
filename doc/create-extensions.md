
- [Creating Extensions](#creating-extensions)
- [General Technical Guide](#general-technical-guide)
  - [Introduction](#introduction)
- [Publishing Extensions](#publishing-extensions)


# Creating Extensions

Creating extensions is handled in two parts:

* General technical details on how to proceed with creating extensions
* Publishing options: private vs public, what it means and the processes involved in each

# General Technical Guide

## Introduction

Please read the [README](https://github.com/nicc777/py-animus) of the `py-animus` project to gain a better understanding of what the project is all about. Extensions are used to implement specific "tasks" that react of a specific kind of manifest and at it's core it is an implementation of the `ManifestBase` class from the `py-animus` project.

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

