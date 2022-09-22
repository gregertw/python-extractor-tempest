Tempest Weather Station Extractor
=================

This repository contains an extractors using the [Cognite Python Extractor Utils
libary](https://github.com/cognitedata/python-extractor-utils).

## Running locally

First, you will need `poetry` installed. You should then be able to run

``` bash
poetry run tempest_extractor <config file>
```

from the command line.

To run the extractor with the provided example config, start by setting the
following environment variables:

* `COGNITE_PROJECT`
* `COGNITE_TOKEN_URL`
* `COGNITE_CLIENT_ID`
* `COGNITE_CLIENT_SECRET`
* `COGNITE_BASE_URL` (can be omitted if your project is hosted at
   `https://api.cognitedata.com`)
* `TEMPEST_TOKEN`
* `TEMPEST_DEVICE_ID`
* `TEMPEST_DEVICE_NAME`
