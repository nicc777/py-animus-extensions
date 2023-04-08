# Creating Private Extensions

Creating private extensions serves two main purposes:

1. During development of an extension, you can develop in an isolated area without affecting any other public extension repositories
2. Perhaps you really want to keep your extension private because of various reasons, for example proprietary intellectual property used in the implementation

Using the example from the [main extensions documentation](./create-extensions.md), the example below will create a private extension.

The key directories and files will be as follow:

| Path                                      | Type      | Description                                                                                           |
|-------------------------------------------|-----------|-------------------------------------------------------------------------------------------------------|
| `/tmp/templates/create-text-file-v1.yaml` | File      | The YAML file containing the definition of our extension - a `AnimusExtensionTemplate` manifest, `v1` |
| `/tmp/test-create-text-file-v1/doc`       | Directory | The directory base for our private extension documentation                                            |
| `/tmp/test-create-text-file-v1/impl`      | Directory | The directory for our private extension implementations                                               |
| `/tmp/test-create-text-file-v1/ex`        | Directory | The directory for our examples for private extensions                                                 |

