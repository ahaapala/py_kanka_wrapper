import requests
from urllib.parse import urlparse

class api_wrapper:

    url          = ""  # API end-point
    method       = ""  # GET or POST
    markup       = ""  # JSON or XML
    auth         = ""  # Credentials for api
    name         = ""
    query_string = ""
    protocol     = ""
    payload      = {} 
    verbose      = True
    content_type = ""
    results      = {}
    headers      = {}

    def __init__(self):
        # No param constructor 
        if self.verbose: print('Constructing API wrapper...')

    def __init__(self, name, url, method='GET'):
        # Details are provided with this one
        if self.verbose: print('Constructing API wrapper w/ parameters...') 
        self.name     = name
        self.url      = url
        self.method   = method

    def make_request(self):
        # Instanciate requests, make the request, and return the results as a string or json object
        if self.method.upper() == "GET":
            response = requests.get(self.url)
        elif self.method.upper() == "POST":
            response = requests.post(self.url, data = self.payload)

        else:
            raise(Exception("Invalid method provided "+self.method.upper()))

        self.results = response.json
        return response.text

    def __repr__(self):
        # How to represent this as a string 
        return "Name: %s, Url: %s, Content-Type: %s, Headers: %s, ".format(self.name,self.url,self.content_type, self.headers)

    def __del__(self):
        if self.verbose: print('Destructing API wrapper...')
