

Command to create new extension structure from extension definitions:

```shell
# Ensure you are in the Python Virtual Environment
# If needed:
pip3 install -r requirements


python3 templates/utils/factory/animus-extension-template.py apply -m $PWD/templates/utils/extension-definitions/REPLACE_ME.yaml -s $PWD/templates/utils/factory
```