# pathofexileTrade
用於抓取市集資料，並協助玩家決策。

## Config
專案會從 [`config.py`](/home/blue/code/pathofexileTrade/config.py) 讀取預設設定，敏感資料則從 `.env` 載入：
- `DEFAULT_LEAGUE`
- `DEFAULT_HEADERS`
- `DEFAULT_COOKIES`
- `REQUEST_TIMEOUT`

先建立 `.env`：

```dotenv
POESESSID=your-session
CF_CLEARANCE=your-clearance
POE_REQUEST_TIMEOUT=30
```

之後可直接修改 `config.py` 的非敏感預設值，或在建立 `POETrade` 時覆蓋：

```python
from pathofexileTrade import POETrade

poe = POETrade()
poe = POETrade("Mirage")
poe = POETrade(cookies={"POESESSID": "...", "cf_clearance": "..."})
```

# TODO
- [x] 抓取功能
- [ ] 定時抓取
- [ ] 特定傳奇或卡片抓取
- [ ] 結合poe.ninja查看當季流派需求物品
