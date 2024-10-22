# 專案名稱

## 簡介

此專案使用 Python 開發，為了方便管理依賴，建議使用虛擬環境 (venv)。請依照以下步驟設定環境並安裝所需套件。

## 安裝與使用說明

1. **Clone 專案**

   打開終端機並執行以下指令：

   ```bash
   git clone https://github.com/julian7862/my_ticket_script.git
   cd my_ticket_script

2. **建立並啟動虛擬環境**

   接著根據你的系統啟動虛擬環境 Linux/macOS：
   ```bash
   source venv/bin/activate

3. **安裝依賴套件**

   虛擬環境啟動後，執行以下指令安裝所需的 Python 套件：
   ```bash
   pip install -r requirements.txt

3. **執行程式**
   
   切換目錄，然後執行主程式
   ```bash
   cd app
   python chrome_tixcraft.py

4. **停用虛擬環境**
   ```bash
   deactivate

## 設定說明

   除了有註解的地方，其他不要亂動
```json
    "homepage": "https://tixcraft.com/activity/game/24_jaychou", //設定要搶票的主頁
    "browser": "chrome",
    "language": "繁體中文",
    "ticket_number": 4, //設定要搶票的張數
    "pass_1_seat_remaining": true,
    "auto_check_agree": true,
    "ocr_captcha": {
      "enable": false,
      "auto_submit": true,
      "force_submit": true
    },
    "tixcraft": {
      "date_auto_select": {
        "enable": true,
        "date_number": 1, //從 0 開始 代表由上往下的日期場次(所以現在 default 第二場)
        "mode": "from top to bottom"
      },
      "area_auto_select": {
        "enable": true,
        "area_keyword_1": "3400", //設定要搶哪個價位的區域
        "area_keyword_2": "",
        "area_keyword_3": "",
        "area_keyword_4": "",
        "mode": "from top to bottom"
      },
      "pass_date_is_sold_out": true,
      "auto_reload_coming_soon_page": true,
      "presale_code": ""
    },
    "advanced": {
      "play_captcha_sound": {
        "enable": true,
        "filename": "ding-dong.wav"
      },
      "facebook_account": "",
      "kktix_account": "",
      "adblock_plus_enable": false
    },
    "debug": false
```
