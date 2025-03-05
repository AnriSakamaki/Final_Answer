from bs4 import BeautifulSoup
from collections import OrderedDict
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

for i in range(1,3):
    if count == 50: break
    target_url = url.format(i)
    time.sleep(3)
    res = requests.get(target_url)

    if res.status_code == 200:
        pass
    else:
        print(f"エラーが発生しました: {res.status_code}")

    soup = BeautifulSoup(res.text, 'html.parser')

    inf_list = []

    contents = soup.find_all("div",class_='style_restaurant__SeIVn')

    #get URL and jump
    for content in contents:
        if count == 50: break
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

        #shop name
        name = soup_url.find(id='info-name', class_='fn org summary').text
        #telephone number
        number = soup_url.find('span', class_='number').text
        #mail
        mail = soup_url.find(id='info_mail')
        if type(mail) == str:
            mail.text
        else:
            pass

        #address
        def divide_address(address):
            pattern = r'^(?P<first_two>.{2})(?P<search>.?[都道府県])(?P<city>.+?)(?=\d)(?P<street>\d{1,3}-\d{1,3}(-\d{1,3}){0,1})(?P<building>.+)?$'
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
            
        full_address = soup_url.find('span', class_='region').text
        test = "兵庫県姫路市立町26 第2八木ビル2F"
        print(test)
        result = divide_address(test)

        prefecture=result["pre"]
        city=result["city"]
        street=result["street"]
        building=result["building"]

        hp_url = None
        url_ssl = None
       
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
        print(inf)
        count += 1
        inf_list.append(inf)
        print(f'proccesing in {count}')
# print("Finish")
# df = pd.DataFrame(inf_list)
# df.columns = ['店舗名', '電話番号', 'メールアドレス','都道府県','市区町村','番地','建物名','URL','SSL']

# df.to_csv("test.csv",index=None,encoding='utf-8-sig')
