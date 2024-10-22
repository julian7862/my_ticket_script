#!/usr/bin/env python3
#encoding=utf-8
# 'seleniumwire' and 'selenium 4' raise error when running python 2.x
# PS: python 2.x will be removed in future.
#執行方式：python chrome_tixcraft.py 或 python3 chrome_tixcraft.py
import os
import sys
import platform
import json
import random

from selenium import webdriver

# chromedrive 隱藏的 type
from selenium_stealth import stealth
import undetected_chromedriver as uc
# for close tab.
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import WebDriverException
# for alert 2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# for selenium 4
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
# for wait #1
import time
import re
from datetime import datetime
# for error output
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('logger')
# for check reg_info
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore',InsecureRequestWarning)

#import tixcraft func
from tixcraft_date_selector import tixcraft_date_auto_select
from tixcraft_area_selector import tixcraft_area_auto_select
from tixcraft_verify import tixcraft_verify
from tixcraft_ticket import tixcraft_ticket_main
from tixcraft_home import tixcraft_home
from facebook_login import facebook_login
# ocr
import base64
# try:
#     import ddddocr
# except Exception as exc:
#     pass

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

CONST_APP_VERSION = u"MaxBot (2023.01.12)3版"

CONST_HOMEPAGE_DEFAULT = "https://tixcraft.com"

CONST_FROM_TOP_TO_BOTTOM = u"from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = u"from bottom to top"
CONST_RANDOM = u"random"
CONST_SELECT_ORDER_DEFAULT = CONST_FROM_TOP_TO_BOTTOM
CONST_SELECT_OPTIONS_DEFAULT = (CONST_FROM_TOP_TO_BOTTOM, CONST_FROM_BOTTOM_TO_TOP, CONST_RANDOM)
CONST_SELECT_OPTIONS_ARRAY = [CONST_FROM_TOP_TO_BOTTOM, CONST_FROM_BOTTOM_TO_TOP, CONST_RANDOM]

CONT_STRING_1_SEATS_REMAINING = [u'@1 seat(s) remaining',u'剩餘 1@',u'@1 席残り']

def get_app_root():
    # 讀取檔案裡的參數值
    # basis = ""
    # if hasattr(sys, 'frozen'):
    #     basis = sys.executable
    # else:
    #     basis = sys.argv[0]
    # app_root = os.path.dirname(basis)
    return ""

def get_config_dict():
    config_json_filename = 'settings.json'
    app_root = get_app_root()
    config_filepath = os.path.join(app_root, config_json_filename)
    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)
    return config_dict



def get_chromedriver_path(webdriver_path):
    chromedriver_path = os.path.join(webdriver_path,"chromedriver")
    # if platform.system().lower()=="windows":
    #     chromedriver_path = os.path.join(webdriver_path,"chromedriver.exe")
    return chromedriver_path


def load_chromdriver_uc(webdriver_path, adblock_plus_enable):

    chromedriver_path = get_chromedriver_path(webdriver_path)

    options = uc.ChromeOptions()
    options.page_load_strategy="eager"

    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-translate')
    options.add_argument('--lang=zh-TW')

    options.add_argument("--password-store=basic")
    options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False})
    options.add_argument('--no-first-run')
    options.add_argument('--no-default-browser-check') 
    # options.add_argument('--user-data-dir=/Users/julian/Library/Application Support/Google/Chrome')
    # options.add_argument('--profile-directory=Profile 4')


    caps = options.to_capabilities()
    caps["unhandledPromptBehavior"] = u"accept"
    driver = None

    print("Use user driver path:", chromedriver_path)
    #driver = uc.Chrome(service=chrome_service, options=options, suppress_welcome=False)
    try:
        driver = uc.Chrome(executable_path=chromedriver_path, options=options, desired_capabilities=caps, suppress_welcome=False)
        # driver = uc.Chrome(executable_path=chromedriver_path, options=options, suppress_welcome=False)
    except Exception as exc:
        print(exc)
        raise

    if driver is None:
        print("create web drive object fail!")
    else:
        download_dir_path="."
        params = {
            "behavior": "allow",
            "downloadPath": os.path.realpath(download_dir_path)
        }
        #print("assign setDownloadBehavior.")
        driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
    #print("driver capabilities", driver.capabilities)

    return driver


def get_driver_by_config(config_dict, driver_type):
    global driver

    homepage = None
    browser = None
    language = "English"
    ticket_number = "2"

    auto_press_next_step_button = False     # default not checked.
    auto_fill_ticket_number = False         # default not checked.
    auto_guess_options = False              # default not checked.

    pass_1_seat_remaining_enable = False        # default not checked.
    pass_date_is_sold_out_enable = False        # default not checked.
    auto_reload_coming_soon_page_enable = True  # default checked.

    area_keyword_1 = ""
    area_keyword_2 = ""
    area_keyword_3 = ""
    area_keyword_4 = ""

    date_keyword = ""

    date_auto_select_enable = None
    date_auto_select_mode = ""

    area_auto_select_enable = None
    area_auto_select_mode = ""

    debugMode = False

    # read config.
    homepage = config_dict["homepage"]
    browser = config_dict["browser"]

    # output debug message in client side.
    debugMode = config_dict["debug"]
    ticket_number = str(config_dict["ticket_number"])
    pass_1_seat_remaining_enable = config_dict["pass_1_seat_remaining"]

    # for ["tixcraft"]
    date_auto_select_enable = config_dict["tixcraft"]["date_auto_select"]["enable"]
    date_auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    if not date_auto_select_mode in CONST_SELECT_OPTIONS_ARRAY:
        date_auto_select_mode = CONST_SELECT_ORDER_DEFAULT

    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()

    area_auto_select_enable = config_dict["tixcraft"]["area_auto_select"]["enable"]
    area_auto_select_mode = config_dict["tixcraft"]["area_auto_select"]["mode"]
    if not area_auto_select_mode in CONST_SELECT_OPTIONS_ARRAY:
        area_auto_select_mode = CONST_SELECT_ORDER_DEFAULT

    area_keyword_1 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_1"].strip()
    area_keyword_2 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_2"].strip()
    area_keyword_3 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_3"].strip()
    area_keyword_4 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_4"].strip()

    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    # output config:
    print("maxbot app version", CONST_APP_VERSION)
    print("python version", platform.python_version())
    print("platform", platform.platform())
    print("homepage", homepage)
    print("browser", browser)
    print("ticket_number", ticket_number)
    print("pass_1_seat_remaining", pass_1_seat_remaining_enable)

    # for tixcraft
    print("==[tixcraft]==")
    print("date_auto_select_enable", date_auto_select_enable)
    print("date_auto_select_mode", date_auto_select_mode)
    print("date_keyword", date_keyword)
    print("pass_date_is_sold_out", pass_date_is_sold_out_enable)
    print("auto_reload_coming_soon_page", auto_reload_coming_soon_page_enable)

    print("area_auto_select_enable", area_auto_select_enable)
    print("area_auto_select_mode", area_auto_select_mode)
    print("area_keyword_1", area_keyword_1)
    print("area_keyword_2", area_keyword_2)
    print("area_keyword_3", area_keyword_3)
    print("area_keyword_4", area_keyword_4)

    print("presale_code", config_dict["tixcraft"]["presale_code"])
    print("ocr_captcha", config_dict['ocr_captcha'])
    print("==[advanced]==")
    print("play_captcha_sound", config_dict["advanced"]["play_captcha_sound"]["enable"])
    print("sound file path", config_dict["advanced"]["play_captcha_sound"]["filename"])
    print("adblock_plus_enable", config_dict["advanced"]["adblock_plus_enable"])
    print("debug Mode", debugMode)

    # entry point
    if homepage is None:
        homepage = ""
    if len(homepage) == 0:
        homepage = CONST_HOMEPAGE_DEFAULT

    Root_Dir = get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    print("platform.system().lower():", platform.system().lower())
    print("webdriver_path:", webdriver_path)
    adblock_plus_enable = config_dict["advanced"]["adblock_plus_enable"]
    print("adblock_plus_enable:", adblock_plus_enable)

    
    if browser == "chrome":
        driver = load_chromdriver_uc(webdriver_path, adblock_plus_enable)
    #print("try to close opened tabs.")
    '''
    time.sleep(1.0)
    for i in range(1):
        close_browser_tabs(driver)
    '''

    if driver is None:
        print("create web driver object fail @_@;")
    else:
        try:
            print("goto url:", homepage)
            # if homepage=="https://tixcraft.com":
            #     homepage="https://tixcraft.com/user/changeLanguage/lang/zh_tw"
            driver.get(homepage)
        except WebDriverException as exce2:
            print('oh no not again, WebDriverException')
            print('WebDriverException:', exce2)
            raise
        except Exception as exec1:
            print('get URL Exception:', exec1)
            raise

    return driver

# from detail to game
def tixcraft_redirect(driver, url):
    ret = False

    game_name = ""

    # get game_name from url
    url_split = url.split("/")
    if len(url_split) >= 6:
        game_name = url_split[5]

    if "/activity/detail/%s" % (game_name,) in url:
        # to support teamear
        entry_url = url.replace("/activity/detail/","/activity/game/")
        print("redirec to new url:", entry_url)
        try:
            driver.get(entry_url)
        except Exception as exec1:
            pass
        ret = True

    return ret
   
def tixcraft_main(driver, url, config_dict, is_verifyCode_editing):
    total_start_time = time.perf_counter()
    logger.info("开始执行 tixcraft_main")

    block1_start = time.perf_counter()
    if 'https://tixcraft.com/' in url:
        logger.info("检测到在首页，调用 tixcraft_home")
        home_start = time.perf_counter()
        tixcraft_home(driver)
        home_end = time.perf_counter()
    logger.info(f"tixcraft_home 执行耗时 {home_end - home_start:.4f} 秒")
    block1_end = time.perf_counter()
    logger.info(f"代码块1(处理首页)耗时 {block1_end - block1_start:.4f} 秒")


    if "/activity/detail/" in url:
        is_redirected = tixcraft_redirect(driver, url)


    block2_start = time.perf_counter()
    if "/activity/game/" in url:
        date_auto_select_enable = config_dict["tixcraft"]["date_auto_select"]["enable"]
        if date_auto_select_enable:
            tixcraft_date_auto_select(driver, url, config_dict)
    block2_end = time.perf_counter()
    logger.info(f"代码块2(選擇日期)耗时 {block2_end - block2_start:.4f} 秒")

    block3_start = time.perf_counter()
    # choose area
    if '/ticket/area/' in url:
        area_auto_select_enable = config_dict["tixcraft"]["area_auto_select"]["enable"]
        if area_auto_select_enable:
            # Replace the old function call
            tixcraft_area_auto_select(driver, url, config_dict)
            print("success")
    block3_end = time.perf_counter()
    logger.info(f"代码块3(选择区域)耗时 {block3_end - block3_start:.4f} 秒")

    # if '/ticket/verify/' in url:
    #     presale_code = config_dict["tixcraft"]["presale_code"]
    #     tixcraft_verify(driver, presale_code)

    # main app, to select ticket number.
    if '/ticket/ticket/' in url:
        if not is_verifyCode_editing:
            is_verifyCode_editing = tixcraft_ticket_main(driver, config_dict)
    else:
        is_verifyCode_editing = False

    return is_verifyCode_editing


def main():
    config_dict = get_config_dict()

    driver_type = 'selenium'
    # driver_type = 'stealth'
    driver_type = 'undetected_chromedriver'

    driver = None
    if not config_dict is None:
        driver = get_driver_by_config(config_dict, driver_type)
    else:
        print("Load config error!")

    # 設定停留時間 3 分鐘
    stay_duration_minutes = 1
    stay_duration_seconds = stay_duration_minutes * 60

    # 每 30 秒發一次 log 提醒，總共持續 3 分鐘
    interval = 30  # 每隔 30 秒
    total_intervals = stay_duration_seconds // interval

    logging.info(f"將停留 {stay_duration_minutes} 分鐘（{stay_duration_seconds} 秒）")

    for i in range(total_intervals):
        time.sleep(interval)
        logging.info(f"已經過了 {(i + 1) * interval} 秒")

    # 記錄停留結束
    logging.info("停留時間已經結束")

    # internal variable. 說明：這是一個內部變數，請略過。
    url = ""

    # for tixcraft
    is_verifyCode_editing = False

    DISCONNECTED_MSG = 'Unable to evaluate script: no such window: target window already closed'

    debugMode = False
    if 'debug' in config_dict:
        debugMode = config_dict["debug"]
    if debugMode:
        print("Start to looping, detect browser url...")

    i = 0
    while True:

        url = ""
        try:
            url = driver.current_url
        except NoSuchWindowException:
            print('NoSuchWindowException at this url:', url )
            #print("last_url:", last_url)
            #print("get_log:", driver.get_log('driver'))
            if DISCONNECTED_MSG in driver.get_log('driver')[-1]['message']:
                print('quit bot by NoSuchWindowException')
                driver.quit()
                sys.exit()
                break
            try:
                window_handles_count = len(driver.window_handles)
                if window_handles_count > 1:
                    driver.switch_to.window(driver.window_handles[0])
            except Exception as excSwithFail:
                pass
        except UnexpectedAlertPresentException as exc1:
            # PS: DON'T remove this line.
            is_verifyCode_editing = False
            print('UnexpectedAlertPresentException at this url:', url )
            #time.sleep(3.5)
            # PS: do nothing...
            # PS: current chrome-driver + chrome call current_url cause alert/prompt dialog disappear!
            # raise exception at selenium/webdriver/remote/errorhandler.py
            # after dialog disappear new excpetion: unhandled inspector error: Not attached to an active page
            is_pass_alert = False
            is_pass_alert = True
            if is_pass_alert:
                try:
                    driver.switch_to.alert.accept()
                except Exception as exc:
                    pass

        except Exception as exc:
            is_verifyCode_editing = False

            logger.error('Maxbot URL Exception')
            logger.error(exc, exc_info=True)

            #UnicodeEncodeError: 'ascii' codec can't encode characters in position 63-72: ordinal not in range(128)
            str_exc = ""
            try:
                str_exc = str(exc)
            except Exception as exc2:
                pass

            if len(str_exc)==0:
                str_exc = repr(exc)

            exit_bot_error_strings = [u'Max retries exceeded'
            , u'chrome not reachable'
            , u'unable to connect to renderer'
            , u'failed to check if window was closed'
            , u'Failed to establish a new connection'
            , u'Connection refused'
            , u'disconnected'
            , u'without establishing a connection'
            , u'web view not found'
            ]
            for each_error_string in exit_bot_error_strings:
                # for python2
                # say goodbye to python2
                '''
                try:
                    basestring
                    if isinstance(each_error_string, unicode):
                        each_error_string = str(each_error_string)
                except NameError:  # Python 3.x
                    basestring = str
                '''
                if isinstance(str_exc, str):
                    if each_error_string in str_exc:
                        print('quit bot by error:', each_error_string)
                        driver.quit()
                        sys.exit()
                        break

            # not is above case, print exception.
            print("Exception:", str_exc)
            pass

        # # for Max's manuall test.
        # if '/Downloads/varify.html' in url:
        #     tixcraft_verify(driver, "")
        # url = "https://tixcraft.com/activity/game/25_maroon5"
        # url = "https://tixcraft.com/activity/game/24_realive"
        if 'tixcraft.com' in url:

            print("Driver: ", driver)
            print("URL: ", url)
            print("Config Dictionary: ", config_dict)
            print("is_verifyCode_editing: ", is_verifyCode_editing)
            # print("OCR: ", ocr)
            is_verifyCode_editing = tixcraft_main(driver, url, config_dict, is_verifyCode_editing)

        i+=1
        print("loop:",i)

if __name__ == "__main__":
    main()


