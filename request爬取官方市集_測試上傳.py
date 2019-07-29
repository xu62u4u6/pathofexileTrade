#!/usr/bin/env python
# coding: utf-8



import requests
import time
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup #整理html資料
import json #處理json資料
from urllib.parse import quote #用於將url中英互換
from fake_useragent import UserAgent #創建假useragent
from math import ceil
import pygsheets




def post_info():
    while True:
        item_name = input("請輸入物品名稱: ")
        item_type = input("請輸入物品類型: ")

        data = {"query":{"status":{"option":"online"}, "name":item_name, "type":item_type,
                         "stats":[{"type":"and","filters":[]}]},"sort":{"price":"asc"}}
        post_url = "https://web.poe.garena.tw/api/trade/search/" + quote(input("請輸入聯盟名稱: ")+"聯盟")#quote將url編碼

        if res.status_code != 200: 
            print("輸入錯誤，請重新輸入")
        else:
            break
    return item_name, item_type, post_url, data




def post_to_url_list(post_url, data) :
    res = requests.post(post_url, json=data)
    soup = BeautifulSoup(res.text, "html5lib") #html5lib最泛用
    post_json = json.loads(soup.text, encoding="utf-8") #將資料轉成json型態

    result, query, total= post_json["result"], post_json["id"], post_json["total"]
    
    url_list = []
    need_times = ceil(len(result)/10) #需要次數假設63/10=6.3，無條件進位 =7次

    for i in range(1, need_times+1): #1 2 3 4 
        url_tmp = "https://web.poe.garena.tw/api/trade/fetch/"

        for iid in range((i-1)*10,i*10): #(0-9), (10-19)
            if iid >= len(result):
                break
            url_tmp += (result[iid] + ",")
        url = url_tmp[:-1] + "?query=" + query#str(iid)#去除最後一個逗點
        url_list.append(url)
    return url_list




def url_list_to_df(url_list) :
    ua = UserAgent() #製造假ua
    df = pd.DataFrame(columns=["amount", "currency", "whisper"], dtype=np.float64)
    count = 0
    for url in url_list:
        res = requests.get(url, headers = {'user-agent': ua.random})
        ud = json.loads(res.text,encoding="utf-8")
        id_list = [i["id"] for i in ud["result"]]
        for i in range(len(id_list)):
            price = ud["result"][i]["listing"]["price"]
            if price != None:
                df.loc[i+count, ['amount','currency']] = price['amount'], price["currency"]
            elif price == None:
                df.loc[i+count, ['amount','currency']] = np.NAN, "None"
            df.loc[i+count, "whisper"] = ud["result"][i]["listing"]['whisper']
            count += 1
    return df



def set_wks(wks):
    wks.cols = 3
    wks.title = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime())
    wks.adjust_column_width(start=2, pixel_size=800)
    return wks



def main():
    item_name, item_type, post_url, data = post_info()
    gc = pygsheets.authorize()
    sh = gc.create(item_name+"_"+item_type)
    wks = set_wks(sh.sheet1)
    for count in range(5):
		print(f"第{count}次執行")
        if count > 0: #第一次不執行
            wks = set_wks(sh.add_worksheet(index=count, title=str(count))) 
        url_list = post_to_url_list(post_url, data)
        df = url_list_to_df(url_list)
        wks.set_dataframe(df, start="A1")
        print(df)
        time.sleep(120)
	print("執行完成")


main()





