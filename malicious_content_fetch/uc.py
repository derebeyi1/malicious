import argparse
import configparser
import os
import pprint

import asyncio
import requests
from datetime import datetime

import time
import logging

from requests.auth import HTTPBasicAuth
from decouple import Config, RepositoryEnv

config = Config(RepositoryEnv(".env"))
parser = argparse.ArgumentParser(description='Query sample information by Hash/Ip/Url/Domain.')
parser.add_argument('--query', dest='query', type=str, help='Query Malicious Hash/Ip/Url/Domain')
# parser.add_argument('--ip', dest='ip', type=str, help='Query Malicious IP')
# parser.add_argument('--ioc', dest='ioc', type=str, help='Query Malicious Hash/IP/URL/Domain')
# parser.add_argument('--schedule', dest='schedule', type=int, help='minute')
parser.add_argument('--username', dest='username', type=str, help='User Name')
parser.add_argument('--api_key', dest='api_key', type=str, help='Api Key')
# parser.add_argument('--query', dest='query', type=str, help='Query Type(malware, malioc, malips)')
args = parser.parse_args()
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
now = datetime.now()
hata_str = ""
name = os.path.splitext(os.path.basename(__file__))[0]

async def UClookup(query):
    conf = configparser.ConfigParser()
    conf.read("settings.ini")
    url = conf.get(name, 'data_url')
    #api_key = config.get(name, 'api_key')
    api_key = config.get('UC_api_key')
    response_json = ''
    while response_json == '':
        try:
            auth = HTTPBasicAuth('admin', api_key)
            response_json = requests.get(url, headers=None, auth=auth, params={'query': query})
            break
        except Exception as e:
            print("hata", e)
            time.sleep(5)
            continue

    print('')
    print("Threat Monitor Info for the Hash/IP/URL/Domain: \n" + query)
    print('#-----------------------------------------------------------------#')
    print('#*******||||||||||||||||||  UC  ||||||||||||||||||*******#')
    print('')
    pprint.pprint(response_json.json(), sort_dicts=False)

if __name__ == '__main__':
    if args.query is None:
        parser.error("--query is required")
    else:
        asyncio.get_event_loop().run_until_complete(UClookup(args.query))