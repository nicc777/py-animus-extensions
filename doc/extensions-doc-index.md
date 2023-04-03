# Extensions Documentation Index

All extensions are defined in the directory `implementations/` where each Python file represents an extension.

All examples are in the directory `examples/` with each sub-directory having the name of the extension (same as the Python source file) and within the extension sub-directory more sub-directories for examples of different scenarios.

```text
examples
└── cli-input-prompt-v1
    ├── basic
    │   └── example.yaml
    ├── minimal
    │   └── example.yaml
    └── password
        └── example.yaml
```

In each scenario sub-directory the manifest will always be named `example.yaml`.

Therefore, when running an example, the following strategy could be used:

```shell
# Use an environment variable to store the extension to test:
export EXTENSION_NAME="cli-input-prompt-v1"

# Use an environment variable to store the scenario to test:
export SCENARIO_NAME="minimal"

# Run the example:
docker run --rm -e "DEBUG=1" -it \
  -v $PWD/implementations:/tmp/src \
  -v $PWD/examples/$EXTENSION_NAME/$SCENARIO_NAME:/tmp/data \
  ghcr.io/nicc777/py-animus:latest apply -m /tmp/data/example.yaml -s /tmp/src
```

> **Note**
> Some examples, like `cli-input-prompt` extension examples, require command line input on the terminal. The docker command is therefore run with the `-it` switch. This could be omitted in most cases as the intention of the system is to run as a script without CLI interaction. However, no harm will come from also just using it all the time.

# Extensions

| Name                                           | Kind             | Description                                             |
|------------------------------------------------|------------------|---------------------------------------------------------|
| [cli-input-prompt-v1](cli-input-prompt-v1.md)  | CliInputPrompt   | Get input from a prompt on the command line from a user |