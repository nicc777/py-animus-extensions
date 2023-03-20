# CliInputPrompt

This manifest, when applied, will prompt a user for some input.

Stores final result in a `Variable` called `CliInputPrompt:<<name-from-manifest>>`.

May have some use where a user needs to supply information, but in these scenarios it will be hard to automate such a process.

```shell
export EXTENSION_NAME="cli-input-prompt"
```

# Spec fields

| Field                              | Type    | Required | In Versions | Description                                                                                                                                                                                                          |
|------------------------------------|:-------:|:--------:|:-----------:|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `spec.promptText`                  | String  | No       | ALL         | The text to display on screen                                                                                                                                                                                        |
| `spec.promptCharacter`             | String  | No       | ALL         | The character for the actual prompt                                                                                                                                                                                  |
| `spec.valueExpires`                | Boolean | No       | ALL         | If set to true, the value will expire after `spec.valueTTL` seconds                                                                                                                                                  |
| `spec.valueTTL`                    | Integer | No       | ALL         | If `spec.valueExpires` is used, use this value to fine tune the exact timeout period in seconds                                                                                                                      |
| `spec.convertEmptyInputToNone`     | Boolean | No       | ALL         | If input is empty, convert the final value to NoneType                                                                                                                                                               |
| `spec.maskInput`                   | Boolean | No       | ALL         | If true, do not echo characters. This is suitable to ask for a password, for example                                                                                                                                 |
| `spec.containsCredentials`         | Boolean | No       | ALL         | If true, set the for_logging=True parameter for the Variable                                                                                                                                                         |

# Example Usages

## Minimal Example

```shell
export SCENARIO_NAME="minimal"
```

Example manifest:

```yaml
---
kind: CliInputPrompt
version: v1
metadata:
  name: get-name-from-cli
```

Will prompt a user for input with the `> ` prompt and store the value.

## Basic Example

```shell
export SCENARIO_NAME="basic"
```

Example manifest:

```yaml
---
kind: CliInputPrompt
version: v1
metadata:
  name: get-name-from-cli
spec:
  promptText: 'What is your name?'
  promptCharacter: 'name > '
```

Will first print on the screen "`What is your name?`" and then prompt a user for input with the `name > ` prompt and store the value.

## Get user credentials Example

```shell
export SCENARIO_NAME="password"
```

Example manifest:

```yaml
---
kind: CliInputPrompt
version: v1
metadata:
  name: get-username-from-cli
  skipApplyAll: true
  skipDeleteAll: true
spec:
  promptText: 'We need your credentials in order to continue'
  promptCharacter: '[get-username-from-cli] username > '
---
kind: CliInputPrompt
version: v1
metadata:
  name: get-password-from-cli
  dependencies:
    apply:
    - get-username-from-cli
  skipDeleteAll: true
spec:
  promptCharacter: '[get-username-from-cli] password > '
  valueExpires: true
  valueTTL: 10
  maskInput: true
  containsCredentials: true

```

A much more complex example where both the username and password for a user must be collected.

The password is marked as sensitive by the `spec.containsCredentials` and in log output only asterisk characters will be printed.

# Versions and Changelog

## Version V1

Initial version