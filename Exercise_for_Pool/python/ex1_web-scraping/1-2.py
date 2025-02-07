from collections import OrderedDict
import csv
import re
import ssl
import socket
import time
from urllib.parse import urlparse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

options = Options()
options.add_argument('--headless')
#service = Service(executable_path="/Users/sakamakian/chromedriver-mac-arm64/chromedriver") 
service = Service(executable_path="/Users/sakamakian/Exercise_for_Pool/python/ex1_web-scraping/1-2/chromedriver") 
driver = webdriver.Chrome(service=service,options=options)

url = 'https://r.gnavi.co.jp/area/jp/rs/'

count = 0
inf_list = []
shop_link_list = []
x = 50


time.sleep(3)
driver.get(url)

while True:
    
    contents = driver.find_elements(By.CSS_SELECTOR,"div.style_restaurant__SeIVn")
    current_url = driver.current_url
    print(f'check{current_url}')
    
    for content in contents:
        link_content = content.find_element(By.CSS_SELECTOR, "a.style_titleLink__oiHVJ")
        if link_content:
            next_link = link_content.get_attribute("href")
            if next_link:
                shop_link_list.append(next_link)
                print(f'link list :{len(shop_link_list)}')
                check = content.find_element(By.CSS_SELECTOR,"h2.style_restaurantNameWrap__wvXSR").text
                print(f'shop name chenk: {check}')

    try:
        if len(shop_link_list) >= x: 
            break
        else:
            next_button = driver.find_element(By.XPATH, f"//a[img[@class='style_nextIcon__M_Me_']]")
            print(next_button)
            next_button.click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.style_restaurant__SeIVn"))
            )

            time.sleep(3)
    except:
        continue


for next_link in shop_link_list:
    if count >= x: break
    print("===============")
    time.sleep(3)
    driver.get(next_link)

    def get_name():
        name = driver.find_element(By.CSS_SELECTOR,"#info-name.fn.org.summary").text
        return name
    
    def get_number():
        number = driver.find_element(By.CSS_SELECTOR, "span.number").text
        return number
    
    def get_mail():
        try:
            mail = driver.find_element(By.ID, "id.info_mail").text
        except NoSuchElementException:
            mail = None
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

        full_address = driver.find_element(By.CSS_SELECTOR,"span.region").text
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
        try:
            building_el = driver.find_element(By.CSS_SELECTOR,"span.locality")
            building = building_el.text.strip()
        except NoSuchElementException:
            building = None
        return building
    
    def get_url():
        try:
            hp_link = driver.find_element(By.CSS_SELECTOR,"a.sv-of.double")
            hp_url = hp_link.get_attribute("href")
        except NoSuchElementException:
            hp_url = None
        return hp_url
    
    def check_ssl_certificate(url):
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else 443

        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    return True
        except Exception as e:
            return False

    
    name = get_name()
    number = get_number()
    mail = get_mail()
    prefecture, city, street, building= get_address()
    hp_url = get_url()
    ssl_sta = check_ssl_certificate(hp_url)


    inf = {
        'name':name,
        'number':number,
        'mail':mail,
        'prefecture':prefecture,
        'city':city,
        'street':street,
        'building':building,
        'url':hp_url,
        'ssl':ssl_sta
    }

    count += 1
    inf_list.append(inf)
    print(f'inf_list size: {len(inf_list)}')
    print(f"processing: {count}")



driver.quit()
df = pd.DataFrame(inf_list)
df.columns = ['店舗名', '電話番号', 'メールアドレス','都道府県','市区町村','番地','建物名','URL','SSL']
df['番地'] = df['番地'].astype(str)
df.to_csv("1-2.csv",index=False,encoding='utf-8-sig',quoting=csv.QUOTE_ALL)
