# __KIND__

__DESCRIPTION__

```shell
export EXTENSION_NAME="__EXTENSION_NAME__"
```

# Spec fields

| Field | Type    | Required | In Versions | Description  |
|-------|:-------:|:--------:|:-----------:|--------------|
__TABLE_ROWS__

# Example Usages

You can run the examples by using the following command after updating your environment variables:

```shell
# Set the examples directory (adjust to suit your needs):
export EXAMPLE_DIR="$PWD/examples"

# If you need to create an output file, also set and mount the output path (adjust to suit your needs):
mkdir /tmp/output
export OUTPUT_PATH=/tmp/output

docker run --rm -e "DEBUG=1" -it \
  -v $PWD/implementations:/tmp/src \
  -v $EXAMPLE_DIR/$EXTENSION_NAME/$SCENARIO_NAME:/tmp/data \
  -v $OUTPUT_PATH:/tmp/output \
  ghcr.io/nicc777/py-animus:latest apply -m /tmp/data/example.yaml -s /tmp/src
```

__PER_SCENARIO_EXAMPLE__

# Versions and Changelog

## Version __VERSION__

Initial content for version __VERSION__
