Weather Extractor
=================

## Sample Extractors using the Python Extractor Util Library

This repository contains two example extractors using the [Cognite Python Extractor Utils
libary](https://github.com/cognitedata/python-extractor-utils):

 * A [CSV extractor](./csv-extractor) reading files on the CSV format and uploading the content to
   CDF RAW
 * A [weather data extractor](./weather-extractor) reading observational data from the The Norwegian
   Meteorological Institute and uploading the data as time series in CDF
 * A sample [Azure IOT Hub extractor](./azure-iot-hub-extractor) polling from Azure IOT Hub and pushing datapoints to CDF

## Weather extractor

This sample extractor queries the publicly available Frost API from The
Norwegian Meteorological Institute for observational data on e.g. temperature,
air pressure or wind speed on a configured set of observational stations.

To use the Frost API, you need to get credentials for it. It a very straight
foreward processs, follow the instructions
[here](https://frost.met.no/auth/requestCredentials.html). You will only need
the client ID for this extractor.

The data from the Frost APIs comes from **The Norwegian Meteorological
Institute**, and is licensed under Norwegian license for public data (NLOD) and
[Creative Commons 4.0](http://creativecommons.org/licenses/by/4.0/).


## Running locally

First, you will need `poetry` installed. You should then be able to run

```
poetry run weather_extractor <config file>
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
 * `FROST_CLIENT_ID`
