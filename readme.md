#### Ryan's Python Napster App
This app implements a basic command line interface for the [Napster Developer API](https://developer.napster.com). It is intended as a quick and dirty utility / API sandbox.

An example usage would be to run `python rypynapa.py -p artists/top?limit=1` to retrieve data on the current top artist on Napster.

The full Napster API is not implemented. The file "rypynapa_api_2.2.json" defines supported APIs and features.

## Dependencies
This code implements the [Napster API v 2.2](https://developer.napster.com/api/v2.2). It was built and tested on MacOS 10.14 / Python 3.7.3.

Package dependencies as a `pip install`:
`pip install requests==2.21.0 urllib3==1.24.1 click==7.0`

## Config
The global config file for API params is "rypynapa_app.cfg." App credentials (`apikey` and `apisecret`) must be set here. **Note**: user authentication (if required) is performed using the password grant method.