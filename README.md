# py_kanka_wrapper

## Table of Contents
+ [About](#about)
+ [Getting Started](#getting_started)
+ [Usage](#usage)

## About <a name = "about"></a>
I have been storing a bunch of rpg story ideas in [Kanka.io](https://kanka.io).  That services has an api.  This library will act as a wrapper and helper for integrating my ttrpg tools with the story content hosted in Kanka.  This could take the form of integrating with the ttrpg_core libraries and/or the chat bot.

## Getting Started <a name = "getting_started"></a>

* Install the requirements.txt file into a virtualenv and run the run_script.py.

### Prerequisites
Check out [requirements.txt](requirements.txt)


## Usage <a name = "usage"></a>

```
usage: run_script.py [-h] [-v] [-u URL] [-n NAME] [-p PAYLOAD]
                     [--headers HEADERS]

Testing script for api wrapper

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         sum the integers (default: find the max)
  -u URL, --url URL     API Endpoint url
  -n NAME, --name NAME  User assigned name of the api
  -p PAYLOAD, --payload PAYLOAD
                        Payload for POST request
  --headers HEADERS     Request Headers
```
