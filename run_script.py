#!/usr/bin/env python
from py_kanka_wrapper.api_wrapper import api_wrapper
import sys
import traceback

def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description='Testing script for api wrapper')
    parser.add_argument('-v','--verbose', dest='verbose', action='store_true',
                        help='sum the integers (default: find the max)')
    parser.add_argument('-u','--url', dest='url', action='store', help='API Endpoint url')
    parser.add_argument('-n','--name', dest='name', action='store', help='User assigned name of the api')
    parser.add_argument('-p','--payload', dest='payload', action='store', help='Payload for POST request')
    parser.add_argument('--headers', dest='headers', action='store', help='Request Headers')

    args = parser.parse_args()

    return args

def main(args):

    name = args.name
    url = args.url

    wrapper = api_wrapper(name,url)
    results = wrapper.make_request()
    print(results)

    return 0

if __name__ == "__main__":
    try:
        args = parse_args()
        main(args)
    except Exception as e:
        print('Script Error:'+str(e))
        traceback.print_exc()
