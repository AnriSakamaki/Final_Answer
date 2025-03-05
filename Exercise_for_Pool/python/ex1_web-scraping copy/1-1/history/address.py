# 〒192-0085  東京都八王子市中町9-5 1F

from bs4 import BeautifulSoup
from collections import OrderedDict
import csv
import re
import requests
import ssl
import socket
import time
from time import sleep
import pandas as pd
from urllib.parse import urlparse


def divide_address(address):
    pattern = r'^(?P<first_two>.{2})(?P<search>.?[都道府県])(?P<city>.+?)(?=\d{1,3}丁目|\d{1,3}-\d{1,3}|\d{1,4})(?P<street>\d{1,4}(-\d{1,3})*)(?=\s|$)(?P<building>.+)?$'
    match = re.match(pattern, address)
    print(match)
    if match:
        result = match.groupdict()
        pre = match.group('first_two') + match.group('search')
        ordered_result = OrderedDict([('pre', pre)] + list(result.items()))
        del ordered_result['first_two']
        del ordered_result['search']
        print(ordered_result)
        return ordered_result
    else:
        return None

def get_address():   
    full_address = "東京都八王子市中町9-5 1F"
    result = divide_address(full_address)

    if result:
        prefecture=result["pre"]
        city=result["city"]
        street=str(result["street"])
        print(type(street))
        building=result["building"].strip()
        print(len(building))
    else:
        prefecture=None
        city=None
        street=None
        building=None

    
    return prefecture,city,street,building

prefecture, city, street, building = get_address()
print(building)



