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

url = 'https://r.gnavi.co.jp/area/jp/rs/?page{}'

count = 0
inf_list = []
x = 50

for i in range(1,3):
    if count == x: break
    target_url = url.format(i)
    time.sleep(3)
    res = requests.get(target_url)

    if res.status_code == 200:
        pass
    else:
        print(f"エラーが発生しました: {res.status_code}")

    soup = BeautifulSoup(res.text, 'html.parser')

    contents = soup.find_all("div",class_='style_restaurant__SeIVn')

    #get URL and jump
    for content in contents:
        if count == x: break
        link_content = content.find('a', class_='style_titleLink__oiHVJ')

        if link_content and 'href' in link_content.attrs:
            next_link = link_content['href']

            time.sleep(3)
            res_next = requests.get(next_link)
            
            if res_next.status_code == 200:
                pass
            else:
                print(f"リンク先でエラーが発生しました: {res_next.status_code}")
        else:
            print("指定したリンクが見つかりませんでした")

        res_next.encoding = 'utf-8'
        soup_url = BeautifulSoup(res_next.text, 'html.parser')

        
        def get_name():
            name = soup_url.find(id='info-name', class_='fn org summary').text
            return name
        
        def get_number():
            number = soup_url.find('span', class_='number').text
            return number
        
        def get_mail():
            mail = soup_url.find(id='info_mail')
            if type(mail) == str:
                mail.text
            else:
                pass

            return mail
        
        def divide_address(address):
            # pattern = r'^(?P<first_two>.{2})(?P<search>.?[都道府県])(?P<city>.+?)(?=\d{1,3}丁目|\d{1,3}-\d{1,3}|\d{1,4})(?P<street>\d{1,4}(-\d{1,3})*)(?=\s|$)(?P<building>.+)?$'
            pattern = r'^(?P<first_two>.{2})(?P<search>.?[都道府県])(?P<city>.+?)(?=\d{1,3}丁目|\d{1,3}-\d{1,3}|\d{1,4})(?P<street>\d{1,4}(-\d{1,3})*)(?=\s|$)$'
            match = re.match(pattern, address)
            if match:
                result = match.groupdict()
                pre = match.group('first_two') + match.group('search')
                ordered_result = OrderedDict([('pre', pre)] + list(result.items()))
                del ordered_result['first_two']
                del ordered_result['search']
                return ordered_result
            else:
                return None

        def get_address():   

            full_address = soup_url.find('span', class_='region').text
            result = divide_address(full_address)
            
            if result:
                prefecture=result["pre"]
                city=result["city"]
                street=str(result["street"])
            else:
                prefecture=None
                city=None
                street=None

            building=get_building()
            
            return prefecture,city,street,building

        def get_building():
            building_el = soup_url.find("span","locality") 
            building = building_el.text.strip() if building_el else None
            return building
        
        hp_url = None
        url_ssl = None
       
        name = get_name()
        number = get_number()
        mail = get_mail()
        prefecture, city, street, building= get_address()


    
        inf = {
            'name':name,
            'number':number,
            'mail':mail,
            'prefecture':prefecture,
            'city':city,
            'street':street,
            'building':building,
            'url':hp_url,
            'ssl':url_ssl
        }

        count += 1
        inf_list.append(inf)
        print(f"processing: {count}")

df = pd.DataFrame(inf_list)
df.columns = ['店舗名', '電話番号', 'メールアドレス','都道府県','市区町村','番地','建物名','URL','SSL']
df['番地'] = df['番地'].astype(str)
df.to_csv("1-1.csv",index=False,encoding='utf-8-sig',quoting=csv.QUOTE_ALL)
