import requests
import json
from urllib.parse import urljoin
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class POETrade:
    def __init__(self, league_name):
        self.search_url = f"https://www.pathofexile.com/api/trade/search/{league_name}"
        self.exchange_url = f"https://www.pathofexile.com/api/trade/exchange/{league_name}"
        self.fetch_url = f"https://www.pathofexile.com/api/trade/fetch/"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
           'Content-Type': 'application/json'}

    def fetch_exchange_data(self, have_item, want_item):
        payload = {"exchange": {
                        "status": {"option": "online"}, 
                        "have": [want_item], 
                        "want": [have_item]
                    }
                }
        res = requests.post(self.exchange_url, data=json.dumps(payload), headers=self.headers)
        if res.status_code != 200:
            return None
        return res.json()

    def fetch_item_data(self, item_name, item_type):
        payload = {
            "query": {
                "status": {
                    "option": "online"
                },
                "name": item_name,
                "type": item_type,
                "stats": [
                    {
                        "type": "and",
                        "filters": [],
                        "disabled": False
                    }
                ]
            },
            "sort": {
                "price": "asc"
            }
        }

        res = requests.post(self.search_url, data=json.dumps(payload), headers=self.headers)
        if res.status_code != 200:
            return None
        return res.json()
    
    def get_items(self, item_name, item_type, max_items_num):
        res_json = self.fetch_item_data(item_name, item_type)
        
        if res_json is None:
            return None
        
        trade_id = res_json["id"]
        results = res_json["result"][:max_items_num]
        
        items_list = []
        for i in range(0, len(results), 10):
            items_url = urljoin(self.fetch_url, ",".join(results[i:i+10]), f"?query={trade_id}")
            res = requests.get(items_url, headers=self.headers)
            if res.status_code != 200:
                items_list.append(None)
            else:
                items_list.extend(res.json()["result"])
        return items_list
    
    def parse_item(self, item):
        account = item["listing"]["account"]
        price = item["listing"]["price"]
        account_name = account["name"]
        last_character_name = account["lastCharacterName"]
        amount = price["amount"]
        currency = price["currency"]
        corrupted = item["item"].get("corrupted", False)     
        return account_name, last_character_name, amount, currency, corrupted
    
    def get_item_df(self, item_name, item_type, max_items_num):
        items = self.get_items(item_name, item_type, max_items_num)
        item_info_list = []
        for item in items:
            item_info_list.append(self.parse_item(item))
        df = pd.DataFrame(item_info_list, columns= ["account_name", "last_character_name", "amount", "currency", "corrupted"])
        return df
    
    def get_exchange_df(self, have_item, want_item):
        res_json = self.fetch_exchange_data(have_item, want_item)
        if res_json is None:
            return None
        result = res_json["result"]
        data = []
        for key, account in result.items():
            account = result[key]["listing"]["account"]
            last_character_name = account["lastCharacterName"]
            account_name = account["name"]
            offer = result[key]["listing"]["offers"][0]
            have_amount = offer["exchange"]["amount"]
            want_amount = offer["item"]["amount"]
            want_stock = offer["item"]["stock"]
            
            data.append([account_name, last_character_name, have_amount, want_amount, want_stock, ])

        df = pd.DataFrame(data, columns=["account_name", "last_character_name", "have_amount", "want_amount", "want_stock"])
        df = df.set_index("account_name")
        df.loc[:, "ratio"] = df.want_amount/df.have_amount
        df.loc[:, "max_num_of_sets"] = df.want_stock//df.want_amount
        return df
    

