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


def post_to_url_list() :
    
    data = {"query":{"status":{"option":"online"}, "name":"七日鋒", "type":"夜語長劍",
                     "stats":[{"type":"and","filters":[]}]},"sort":{"price":"asc"}}
    
    post_url = "https://web.poe.garena.tw/api/trade/search/" + quote("戰亂聯盟")#quote將url編碼
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



def get_wks():
    gc = pygsheets.authorize()
    
    strtime_now = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime())
    file_name = "七日鋒_夜語長劍"
    
    try: #測試是否存在
        sh = gc.open(file_name)
    except: #不存在的話，建立一個檔案，並且將sheet1設定為當前時間
        sh = gc.create(file_name)
        wks = sh.sheet1
        wks.title = strtime_now
    else: #有找到檔案則新建一個工作表，index = 當前工作表數量
        wks = sh.add_worksheet(index=len(sh.worksheets()), title=strtime_now)
    finally:
        wks.cols = 3 
        wks.adjust_column_width(start=2, pixel_size=800) #設定whisper的寬度
    return wks



def del_all_gsheet_by_filename(file_name):
    while True:
        try:
            sh = gc.open(file_name)
            sh.delete()
        except:
            print("完成")
            break




def main():
    wks = get_wks()
    url_list = post_to_url_list()
    df = url_list_to_df(url_list)
    wks.set_dataframe(df, start="A1") #將dataframe自A1




if __name__ == "__main__":
    main()

