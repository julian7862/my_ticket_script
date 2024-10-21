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
logging.basicConfig()
logger = logging.getLogger('logger')
# for check reg_info
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore',InsecureRequestWarning)

#import tixcraft func
from tixcraft_date_selector import tixcraft_date_auto_select
from tixcraft_area_selector import tixcraft_area_auto_select

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

def find_continuous_number(text):
    chars = "0123456789"
    return find_continuous_pattern(chars, text)

def find_continuous_text(text):
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return find_continuous_pattern(chars, text)

def find_continuous_pattern(allowed_char, text):
    ret = ""
    is_allowed_char_start = False
    for char in text:
        #print("char:", char)
        if char in allowed_char:
            if len(ret)==0 and not is_allowed_char_start:
                is_allowed_char_start = True
            if is_allowed_char_start:
                ret += char
        else:
            # make not continuous
            is_allowed_char_start = False
    return ret

def get_favoriate_extension_path(webdriver_path):
    no_google_analytics_path = os.path.join(webdriver_path,"no_google_analytics_1.1.0.0.crx")
    no_ad_path = os.path.join(webdriver_path,"Adblock_3.15.2.0.crx")
    return no_google_analytics_path, no_ad_path

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

def close_browser_tabs(driver):
    if not driver is None:
        try:
            window_handles_count = len(driver.window_handles)
            if window_handles_count > 1:
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except Exception as excSwithFail:
            pass

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
        # method 6: Selenium Stealth
        # if driver_type != "undetected_chromedriver":
        #     driver = load_chromdriver_normal(webdriver_path, driver_type, adblock_plus_enable)
        # else:
            # # method 5: uc
            # # multiprocessing not work bug.
            # if platform.system().lower()=="windows":
            #     if hasattr(sys, 'frozen'):
            #         from multiprocessing import freeze_support
            #         freeze_support()
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

# common functions.
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

# convert web string to reg pattern
def convert_string_to_pattern(my_str, dynamic_length=True):
    my_hint_anwser_length = len(my_str)
    my_formated = ""
    if my_hint_anwser_length > 0:
        my_anwser_symbols = u"()[]<>{}-"
        for idx in range(my_hint_anwser_length):
            char = my_str[idx:idx+1]

            if char in my_anwser_symbols:
                my_formated += (u'\\' + char)
                continue

            pattern = re.compile(u"[A-Z]")
            match_result = pattern.match(char)
            #print("match_result A:", match_result)
            if not match_result is None:
                my_formated += u"[A-Z]"

            pattern = re.compile(u"[a-z]")
            match_result = pattern.match(char)
            #print("match_result a:", match_result)
            if not match_result is None:
                my_formated += u"[a-z]"

            pattern = re.compile(u"[\d]")
            match_result = pattern.match(char)
            #print("match_result d:", match_result)
            if not match_result is None:
                my_formated += u"[\d]"

        # for dynamic length
        if dynamic_length:
            for i in range(10):
                my_formated = my_formated.replace(u"[A-Z][A-Z]",u"[A-Z]")
                my_formated = my_formated.replace(u"[a-z][a-z]",u"[a-z]")
                my_formated = my_formated.replace(u"[\d][\d]",u"[\d]")

            my_formated = my_formated.replace(u"[A-Z]",u"[A-Z]+")
            my_formated = my_formated.replace(u"[a-z]",u"[a-z]+")
            my_formated = my_formated.replace(u"[\d]",u"[\d]+")
    return my_formated

def guess_answer_list_from_multi_options(tmp_text):
    options_list = None
    if options_list is None:
        if u'【' in tmp_text and u'】' in tmp_text:
            options_list = re.findall(u'【.*?】', tmp_text)
            if len(options_list) <= 2:
                options_list = None

    if options_list is None:
        if u'(' in tmp_text and u')' in tmp_text:
            options_list = re.findall(u'\(.*?\)', tmp_text)
            if len(options_list) <= 2:
                options_list = None

    if options_list is None:
        if u'[' in tmp_text and u']' in tmp_text:
            options_list = re.findall(u'[.*?]', tmp_text)
            if len(options_list) <= 2:
                options_list = None

    return_list = None
    if not options_list is None:
        options_list_length = len(options_list)
        if options_list_length > 2:
            is_all_options_same_length = True
            for i in range(options_list_length-1):
                if len(options_list[i]) != len(options_list[i]):
                    is_all_options_same_length = False

            if is_all_options_same_length:
                return_list = []
                for each_option in options_list:
                    return_list.append(each_option[1:-1])
    return return_list

#PS: this may get a wrong answer list. XD
def guess_answer_list_from_symbols(captcha_text_div_text):
    return_list = None
    # need replace to space to get first options.
    tmp_text = captcha_text_div_text
    tmp_text = tmp_text.replace(u'?',u' ')
    tmp_text = tmp_text.replace(u'？',u' ')
    tmp_text = tmp_text.replace(u'。',u' ')

    delimitor_symbols_left = [u"(",u"[",u"{", " ", " ", " ", " "]
    delimitor_symbols_right = [u")",u"]",u"}", ":", ".", ")", "-"]
    idx = -1
    for idx in range(len(delimitor_symbols_left)):
        symbol_left = delimitor_symbols_left[idx]
        symbol_right = delimitor_symbols_right[idx]
        if symbol_left in tmp_text and symbol_right in tmp_text and u'半形' in tmp_text:
            hint_list = re.findall(u'\\'+ symbol_left + u'[\\w]+\\'+ symbol_right , tmp_text)
            #print("hint_list:", hint_list)
            if not hint_list is None:
                if len(hint_list) > 1:
                    return_list = []
                    my_answer_delimitor = symbol_right
                    for options in hint_list:
                        if len(options) > 2:
                            my_anwser = options[1:-1]
                            #print("my_anwser:",my_anwser)
                            if len(my_anwser) > 0:
                                return_list.append(my_anwser)

        if not return_list is None:
            break
    return return_list

def get_offical_hint_string_from_symbol(symbol, tmp_text):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    offical_hint_string = ""
    if symbol in tmp_text:
        # start to guess offical hint
        if offical_hint_string == "":
            if u'【' in tmp_text and u'】' in tmp_text:
                hint_list = re.findall(u'【.*?】', tmp_text)
                if not hint_list is None:
                    if show_debug_message:
                        print("【.*?】hint_list:", hint_list)
                    for hint in hint_list:
                        if symbol in hint:
                            offical_hint_string = hint[1:-1]
                            break
        if offical_hint_string == "":
            if u'(' in tmp_text and u')' in tmp_text:
                hint_list = re.findall(u'\(.*?\)', tmp_text)
                if not hint_list is None:
                    if show_debug_message:
                        print("\(.*?\)hint_list:", hint_list)
                    for hint in hint_list:
                        if symbol in hint:
                            offical_hint_string = hint[1:-1]
                            break
        if offical_hint_string == "":
            if u'[' in tmp_text and u']' in tmp_text:
                hint_list = re.findall(u'[.*?]', tmp_text)
                if not hint_list is None:
                    if show_debug_message:
                        print("[.*?]hint_list:", hint_list)
                    for hint in hint_list:
                        if symbol in hint:
                            offical_hint_string = hint[1:-1]
                            break
        if offical_hint_string == "":
            offical_hint_string = tmp_text
    return offical_hint_string

def guess_answer_list_from_hint(CONST_EXAMPLE_SYMBOL, captcha_text_div_text):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    CONST_INPUT_SYMBOL = '輸入'

    return_list = None

    tmp_text = format_question_string(CONST_EXAMPLE_SYMBOL, captcha_text_div_text)

    my_question = ""
    my_options = ""
    offical_hint_string = ""
    offical_hint_string_anwser = ""
    my_anwser_formated = ""
    my_answer_delimitor = ""

    if my_question == "":
        if u"?" in tmp_text:
            question_index = tmp_text.find(u"?")
            my_question = tmp_text[:question_index+1]
    if my_question == "":
        if u"。" in tmp_text:
            question_index = tmp_text.find(u"。")
            my_question = tmp_text[:question_index+1]
    if my_question == "":
        my_question = tmp_text
    #print(u"my_question:", my_question)

    # ps: hint_list is not options list

    if offical_hint_string == "":
        offical_hint_string = get_offical_hint_string_from_symbol(CONST_EXAMPLE_SYMBOL, tmp_text)
        if len(offical_hint_string) > 0:
            right_part = offical_hint_string.split(CONST_EXAMPLE_SYMBOL)[1]
            if len(offical_hint_string) == len(tmp_text):
                offical_hint_string = right_part

            new_hint = find_continuous_text(right_part)
            if len(new_hint) > 0:
                offical_hint_string_anwser = new_hint

    if offical_hint_string == "":
        # for: 若你覺得答案為 a，請輸入 a
        if '答案' in tmp_text and CONST_INPUT_SYMBOL in tmp_text:
            offical_hint_string = get_offical_hint_string_from_symbol(CONST_INPUT_SYMBOL, tmp_text)
        if len(offical_hint_string) > 0:
            right_part = offical_hint_string.split(CONST_INPUT_SYMBOL)[1]
            if len(offical_hint_string) == len(tmp_text):
                offical_hint_string = right_part

            new_hint = find_continuous_text(right_part)
            if len(new_hint) > 0:
                # TODO: 答案為B需填入Bb)
                #if u'答案' in offical_hint_string and CONST_INPUT_SYMBOL in offical_hint_string:
                offical_hint_string_anwser = new_hint

    if show_debug_message:
        print("offical_hint_string:",offical_hint_string)

    # try rule4:
    # get hint from rule 3: without '(' & '), but use "*"
    if len(offical_hint_string) == 0:
        target_symbol = u"*"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index + len(target_symbol))
            offical_hint_string = tmp_text[star_index: space_index]

    # is need to merge next block
    if len(offical_hint_string) > 0:
        target_symbol = offical_hint_string + u" "
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            next_block_index = star_index + len(target_symbol)
            space_index = tmp_text.find(u" ", next_block_index)
            next_block = tmp_text[next_block_index: space_index]
            if CONST_EXAMPLE_SYMBOL in next_block:
                offical_hint_string += u' ' + next_block

    # try rule5:
    # get hint from rule 3: n個半形英文大寫
    if len(offical_hint_string) == 0:
        target_symbol = u"個半形英文大寫"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                offical_hint_string_anwser = u'A' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個英文大寫"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                offical_hint_string_anwser = u'A' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個半形英文小寫"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                offical_hint_string_anwser = u'a' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個英文小寫"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                offical_hint_string_anwser = u'a' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個英數半形字"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                my_anwser_formated = u'[A-Za-z\d]' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個半形"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                my_anwser_formated = u'[A-Za-z\d]' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

    if len(offical_hint_string) > 0:
        #print("offical_hint_string_anwser:", offical_hint_string_anwser)
        my_anwser_formated = convert_string_to_pattern(offical_hint_string_anwser)

    my_options = tmp_text
    if len(my_question) < len(tmp_text):
        my_options = my_options.replace(my_question,u"")
    my_options = my_options.replace(offical_hint_string,u"")
    #print("tmp_text:", tmp_text)
    #print("my_options:", my_options)
    #print("offical_hint_string:", offical_hint_string)

    # try rule7:
    # check is chinese/english in question, if match, apply my_options rule.
    if len(offical_hint_string) > 0:
        tmp_text_org = captcha_text_div_text
        if CONST_EXAMPLE_SYMBOL in tmp_text:
            tmp_text_org = tmp_text_org.replace(u'Ex:','ex:')
            target_symbol = u"ex:"
            if target_symbol in tmp_text_org :
                star_index = tmp_text_org.find(target_symbol)
                my_options = tmp_text_org[star_index-1:]

    #print(u"my_options:", my_options)

    if len(my_anwser_formated) > 0:
        allow_delimitor_symbols = ")].: }"
        pattern = re.compile(my_anwser_formated)
        search_result = pattern.search(my_options)
        if not search_result is None:
            (span_start, span_end) = search_result.span()
            if len(my_options) > (span_end+1)+1:
                maybe_delimitor = my_options[span_end+0:span_end+1]
            if maybe_delimitor in allow_delimitor_symbols:
                my_answer_delimitor = maybe_delimitor
    #print(u"my_answer_delimitor:", my_answer_delimitor)

    if len(my_anwser_formated) > 0:
        #print("text:" , re.findall('\([\w]+\)', tmp_text))
        new_pattern = my_anwser_formated
        if len(my_answer_delimitor) > 0:
            new_pattern = my_anwser_formated + u'\\' + my_answer_delimitor
        return_list = re.findall(new_pattern, my_options)

        if not return_list is None:
            if len(return_list) == 1:
                # re-sample for this case.
                return_list = re.findall(my_anwser_formated, my_options)

    return return_list

def format_question_string(CONST_EXAMPLE_SYMBOL, captcha_text_div_text):
    CONST_INPUT_SYMBOL = '輸入'

    tmp_text = captcha_text_div_text
    tmp_text = tmp_text.replace(u'  ',u' ')
    tmp_text = tmp_text.replace(u'：',u':')
    # for hint
    tmp_text = tmp_text.replace(u'*',u'*')

    # replace ex.
    tmp_text = tmp_text.replace(u'例如', CONST_EXAMPLE_SYMBOL)
    tmp_text = tmp_text.replace(u'如:', CONST_EXAMPLE_SYMBOL)
    tmp_text = tmp_text.replace(u'舉例', CONST_EXAMPLE_SYMBOL)
    if not CONST_EXAMPLE_SYMBOL in tmp_text:
        tmp_text = tmp_text.replace(u'例', CONST_EXAMPLE_SYMBOL)
    # important, maybe 例 & ex occurs at same time.
    tmp_text = tmp_text.replace(u'ex:', CONST_EXAMPLE_SYMBOL)
    tmp_text = tmp_text.replace(u'Ex:', CONST_EXAMPLE_SYMBOL)

    #若你覺得
    #PS:這個，可能會造成更多問題，呵呵。
    SYMBOL_IF_LIST = ['假設','如果','若']
    for symbol_if in SYMBOL_IF_LIST:
        if symbol_if in tmp_text and '答案' in tmp_text:
            tmp_text = tmp_text.replace('覺得', '')
            tmp_text = tmp_text.replace('認為', '')
            tmp_text = tmp_text.replace(symbol_if + '你答案', CONST_EXAMPLE_SYMBOL + '答案')
            tmp_text = tmp_text.replace(symbol_if + '答案', CONST_EXAMPLE_SYMBOL + '答案')

    tmp_text = tmp_text.replace(u'填入', CONST_INPUT_SYMBOL)

    #tmp_text = tmp_text.replace(u'[',u'(')
    #tmp_text = tmp_text.replace(u']',u')')
    tmp_text = tmp_text.replace(u'？',u'?')

    tmp_text = tmp_text.replace(u'（',u'(')
    tmp_text = tmp_text.replace(u'）',u')')

    return tmp_text

def get_answer_list_by_question(CONST_EXAMPLE_SYMBOL, captcha_text_div_text):
    return_list = None

    tmp_text = format_question_string(CONST_EXAMPLE_SYMBOL, captcha_text_div_text)

    # guess answer list from multi-options: 【】() []
    if return_list is None:
        return_list = guess_answer_list_from_multi_options(tmp_text)
        pass

    if return_list is None:
        return_list = guess_answer_list_from_hint(CONST_EXAMPLE_SYMBOL, captcha_text_div_text)

    # try rule8:
    if return_list is None:
        return_list = guess_answer_list_from_symbols(captcha_text_div_text)

    return return_list

# close some div on home url.
def tixcraft_home(driver):
    print("一日遊")
    accept_all_cookies_btn = None
    try:
        accept_all_cookies_btn = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
    except Exception as exc:
        #print("find accept_all_cookies_btn fail")
        pass

    if accept_all_cookies_btn is not None:
        is_visible = False
        try:
            if accept_all_cookies_btn.is_enabled() and accept_all_cookies_btn.is_displayed():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            try:
                accept_all_cookies_btn.click()
            except Exception as exc:
                print("try to click accept_all_cookies_btn fail")
                try:
                    driver.execute_script("arguments[0].click();", accept_all_cookies_btn)
                except Exception as exc:
                    pass

    close_all_alert_btns = None
    try:
        close_all_alert_btns = driver.find_elements(By.CSS_SELECTOR, "[class='close-alert']")
    except Exception as exc:
        print("find close_all_alert_btns fail")

    if close_all_alert_btns is not None:
        #print('alert count:', len(close_all_alert_btns))
        for alert_btn in close_all_alert_btns:
            # fix bug: Message: stale element reference: element is not attached to the page document
            is_visible = False
            try:
                if alert_btn.is_enabled() and alert_btn.is_displayed():
                    is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    alert_btn.click()
                except Exception as exc:
                    print("try to click alert_btn fail")
                    try:
                        driver.execute_script("arguments[0].click();", alert_btn)
                    except Exception as exc:
                        pass

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

# def tixcraft_date_auto_select(driver, url, config_dict):
#     show_debug_message = True    # debug.
#     show_debug_message = False   # online

#     # read config.
#     date_auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
#     date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
#     pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
#     auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

#     # PS: for big events, check sold out text maybe not helpful, due to database is too busy.
#     sold_out_text_list = ["選購一空","No tickets available","空席なし"]

#     game_name = ""

#     if "/activity/game/" in url:
#         url_split = url.split("/")
#         if len(url_split) >= 6:
#             game_name = url_split[5]

#     if show_debug_message:
#         print('get date game_name:', game_name)
#         print("date_auto_select_mode:", date_auto_select_mode)
#         print("date_keyword:", date_keyword)

#     check_game_detail = False
#     # choose date
#     if "/activity/game/%s" % (game_name,) in url:
#         if show_debug_message:
#             if len(date_keyword) == 0:
#                 print("date keyword is empty.")
#             else:
#                 print("date keyword:", date_keyword)
#         check_game_detail = True

#     date_list = None
#     if check_game_detail:
#         try:
#             date_list = driver.find_elements(By.CSS_SELECTOR, '#gameList > table > tbody > tr')
#         except Exception as exc:
#             print("find #gameList fail")

#     is_coming_soon = False
#     coming_soon_condictions_list = ['開賣','剩餘','天','小時','分鐘','秒','0',':','/']
    
#     button_list = None
#     if date_list is not None:
#         button_list = []
#         for row in date_list:
#             # step 1: check keyword.
#             is_match_keyword_row = False

#             row_text = ""
#             try:
#                 row_text = row.text
#             except Exception as exc:
#                 print("get text fail")
#                 # should use continue or break?
#                 break

#             if row_text is None:
#                 row_text = ""

#             if len(row_text) > 0:
#                 is_match_all_coming_soon_condiction = True
#                 for condiction_string in coming_soon_condictions_list:
#                     if not condiction_string in row_text:
#                         is_match_all_coming_soon_condiction = False
#                         break
#                 if is_match_all_coming_soon_condiction:
#                     is_coming_soon = True
#                     break

#                 if len(date_keyword) == 0:
#                     # no keyword, match all.
#                     is_match_keyword_row = True
#                 else:
#                     # check keyword.
#                     if date_keyword in row_text:
#                         is_match_keyword_row = True

#             # step 2: check sold out.
#             if is_match_keyword_row:
#                 if pass_date_is_sold_out_enable:
#                     for sold_out_item in sold_out_text_list:
#                         row_text_right_part = row_text[(len(sold_out_item)+5)*-1:]
#                         if show_debug_message:
#                             print("check right part text:", row_text_right_part)
#                         if sold_out_item in row_text_right_part:
#                             is_match_keyword_row = False

#                             if show_debug_message:
#                                 print("match sold out text: %s, skip this row." % (sold_out_item))

#                             # no need check next language item.
#                             break

#             # step 3: add to list.
#             if is_match_keyword_row:
#                 el = None
#                 try:
#                     el = row.find_element(By.CSS_SELECTOR, '.btn-next')
#                 except Exception as exc:
#                     if show_debug_message:
#                         print("find .btn-next fail")
#                     pass

#                 if el is not None:
#                     button_list.append(el)
#                     if date_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
#                         # only need one row.
#                         if show_debug_message:
#                             print("match date row, only need first row, start to break")
#                         break

#     is_date_selected = False
#     if button_list is not None:
#         if len(button_list) > 0:
#             # default first row.
#             target_row_index = 0

#             if date_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
#                 target_row_index = len(button_list) - 1

#             if date_auto_select_mode == CONST_RANDOM:
#                 target_row_index = random.randint(0,len(button_list)-1)

#             if show_debug_message:
#                 print("clicking row:", target_row_index+1)

#             try:
#                 el = button_list[target_row_index]
#                 el.click()
#                 is_date_selected = True
#             except Exception as exc:
#                 print("try to click .btn-next fail")
#                 try:
#                     driver.execute_script("arguments[0].click();", el)
#                 except Exception as exc:
#                     pass

#         # PS: Is this case need to reload page?
#         #   (A)user input keywords, with matched text, but no hyperlink to click.
#         #   (B)user input keywords, but not no matched text with hyperlink to click.

#     # [PS]: current reload condition only when 
#     if auto_reload_coming_soon_page_enable:
#         if is_coming_soon:
#             # case 2: match one row is coming soon.
#             try:
#                 driver.refresh()
#             except Exception as exc:
#                 pass
#         else:
#             if not is_date_selected:
#                 # case 1: No hyperlink button.
#                 el_list = None
#                 try:
#                     el_list = driver.find_elements(By.CSS_SELECTOR, '.btn-next')
#                     if el_list is None:
#                         driver.refresh()
#                     else:
#                         if len(el_list) == 0:
#                             driver.refresh()
#                 except Exception as exc:
#                     pass

#     return is_date_selected

# PURPOSE: get target area list.
# RETURN:
#   is_need_refresh
#   matched_blocks
# PS: matched_blocks will be None, if length equals zero.
# def get_tixcraft_target_area(el, area_keyword, area_auto_select_mode, pass_1_seat_remaining_enable):
#     show_debug_message = True       # debug.
#     show_debug_message = False      # online

#     is_need_refresh = False
#     matched_blocks = None

#     area_list = None
#     area_list_count = 0
#     if el is not None:
#         try:
#             area_list = el.find_elements(By.TAG_NAME, 'a')
#         except Exception as exc:
#             #print("find area list a tag fail")
#             pass

#         if area_list is not None:
#             area_list_count = len(area_list)
#             if area_list_count == 0:
#                 print("area list is empty, do refresh!")
#                 is_need_refresh = True
#         else:
#             print("area list is None, do refresh!")
#             is_need_refresh = True

#     if area_list_count > 0:
#         matched_blocks = []
#         for row in area_list:
#             row_is_enabled=False
#             try:
#                 row_is_enabled = row.is_enabled()
#             except Exception as exc:
#                 pass

#             row_text = ""
#             if row_is_enabled:
#                 try:
#                     row_text = row.text
#                 except Exception as exc:
#                     print("get text fail")
#                     break

#             if row_text is None:
#                 row_text = ""

#             if len(row_text) > 0:
#                 # clean stop word.
#                 row_text = format_keyword_string(row_text)

#                 is_append_this_row = False

#                 if len(area_keyword) > 0:
#                     # clean stop word.
#                     area_keyword = format_keyword_string(area_keyword)

#                 # allow only input stop word in keyword fields.
#                 # for keyword#2 to select all.
#                 if len(area_keyword) > 0:
#                     # must match keyword.
#                     if area_keyword in row_text:
#                         is_append_this_row = True
#                 else:
#                     # without keyword.
#                     is_append_this_row = True

#                 if is_append_this_row:
#                     if show_debug_message:
#                         print("pass_1_seat_remaining_enable:", pass_1_seat_remaining_enable)
#                     if pass_1_seat_remaining_enable:
#                         area_item_font_el = None
#                         try:
#                             #print('try to find font tag at row:', row_text)
#                             area_item_font_el = row.find_element(By.TAG_NAME, 'font')
#                             if not area_item_font_el is None:
#                                 font_el_text = area_item_font_el.text
#                                 if font_el_text is None:
#                                     font_el_text = ""
#                                 font_el_text = "@%s@" % (font_el_text)
#                                 if show_debug_message:
#                                     print('font tag text:', font_el_text)
#                                     pass
#                                 for check_item in CONT_STRING_1_SEATS_REMAINING:
#                                     if check_item in font_el_text:
#                                         if show_debug_message:
#                                             print("match pass 1 seats remaining 1 full text:", row_text)
#                                             print("match pass 1 seats remaining 2 font text:", font_el_text)
#                                         is_append_this_row = False
#                             else:
#                                 #print("row withou font tag.")
#                                 pass
#                         except Exception as exc:
#                             #print("find font text in a tag fail:", exc)
#                             pass

#                 if show_debug_message:
#                     print("is_append_this_row:", is_append_this_row)

#                 if is_append_this_row:
#                     matched_blocks.append(row)

#                     if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
#                         print("only need first item, break area list loop.")
#                         break
#                     if show_debug_message:
#                         print("row_text:" + row_text)
#                         print("match:" + area_keyword)

#         if len(matched_blocks) == 0:
#             matched_blocks = None
#             is_need_refresh = True

#     return is_need_refresh, matched_blocks

# PS: auto refresh condition 1: no keyword + no hyperlink.
# PS: auto refresh condition 2: with keyword + no hyperlink.
# def tixcraft_area_auto_select(driver, url, config_dict):
#     show_debug_message = True       # debug.
#     show_debug_message = False      # online

#     # read config.
#     area_keyword_1 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_1"].strip()
#     area_keyword_2 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_2"].strip()
#     area_keyword_3 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_3"].strip()
#     area_keyword_4 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_4"].strip()
#     area_auto_select_mode = config_dict["tixcraft"]["area_auto_select"]["mode"]

#     pass_1_seat_remaining_enable = config_dict["pass_1_seat_remaining"]
#     # disable pass 1 seat remaining when target ticket number is 1.
#     ticket_number = config_dict["ticket_number"]
#     if ticket_number == 1:
#         pass_1_seat_remaining_enable = False

#     if show_debug_message:
#         print("area_keyword_1, area_keyword_2:", area_keyword_1, area_keyword_2)
#         print("area_keyword_3, area_keyword_4:", area_keyword_3, area_keyword_4)

#     if '/ticket/area/' in url:
#         #driver.switch_to.default_content()

#         el = None
#         try:
#             el = driver.find_element(By.CSS_SELECTOR, '.zone')
#         except Exception as exc:
#             print("find .zone fail, do nothing.")

#         if el is not None:
#             is_need_refresh, areas = get_tixcraft_target_area(el, area_keyword_1, area_auto_select_mode, pass_1_seat_remaining_enable)
#             if show_debug_message:
#                 print("is_need_refresh for keyword1:", is_need_refresh)

#             if is_need_refresh:
#                 if areas is None:
#                     if show_debug_message:
#                         print("use area keyword #2", area_keyword_2)

#                     # only when keyword#2 filled to query.
#                     if len(area_keyword_2) > 0 :
#                         is_need_refresh, areas = get_tixcraft_target_area(el, area_keyword_2, area_auto_select_mode, pass_1_seat_remaining_enable)
#                         if show_debug_message:
#                             print("is_need_refresh for keyword2:", is_need_refresh)

#             if is_need_refresh:
#                 if areas is None:
#                     if show_debug_message:
#                         print("use area keyword #3", area_keyword_3)

#                     # only when keyword#3 filled to query.
#                     if len(area_keyword_3) > 0 :
#                         is_need_refresh, areas = get_tixcraft_target_area(el, area_keyword_3, area_auto_select_mode, pass_1_seat_remaining_enable)
#                         if show_debug_message:
#                             print("is_need_refresh for keyword3:", is_need_refresh)

#             if is_need_refresh:
#                 if areas is None:
#                     if show_debug_message:
#                         print("use area keyword #4", area_keyword_4)

#                     # only when keyword#4 filled to query.
#                     if len(area_keyword_4) > 0 :
#                         is_need_refresh, areas = get_tixcraft_target_area(el, area_keyword_4, area_auto_select_mode, pass_1_seat_remaining_enable)
#                         if show_debug_message:
#                             print("is_need_refresh for keyword4:", is_need_refresh)

#             area_target = None
#             if areas is not None:
#                 #print("area_auto_select_mode", area_auto_select_mode)
#                 #print("len(areas)", len(areas))
#                 if len(areas) > 0:
#                     target_row_index = 0

#                     if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
#                         pass

#                     if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
#                         target_row_index = len(areas)-1

#                     if area_auto_select_mode == CONST_RANDOM:
#                         target_row_index = random.randint(0,len(areas)-1)

#                     #print("target_row_index", target_row_index)
#                     area_target = areas[target_row_index]

#             if area_target is not None:
#                 try:
#                     #print("area text:", area_target.text)
#                     area_target.click()
#                 except Exception as exc:
#                     print("click area a link fail, start to retry...")
#                     try:
#                         driver.execute_script("arguments[0].click();", area_target)
#                     except Exception as exc:
#                         print("click area a link fail, after reftry still fail.")
#                         print(exc)
#                         pass

#             # auto refresh for area list page.
#             if is_need_refresh:
#                 try:
#                     driver.refresh()
#                 except Exception as exc:
#                     pass

# '''
#         el_selectSeat_iframe = None
#         try:
#             el_selectSeat_iframe = driver.find_element_by_xpath("//iframe[contains(@src,'/ticket/selectSeat/')]")
#         except Exception as exc:
#             #print("find seat iframe fail")
#             pass

#         if el_selectSeat_iframe is not None:
#             driver.switch_to.frame(el_selectSeat_iframe)

#             # click one seat
#             el_seat = None
#             try:
#                 el_seat = driver.find_element(By.CSS_SELECTOR, '.empty')
#                 if el_seat is not None:
#                     try:
#                         el_seat.click()
#                     except Exception as exc:
#                         #print("click area button fail")
#                         pass
#             except Exception as exc:
#                 print("find empty seat fail")


#             # click submit button
#             el_confirm_seat = None
#             try:
#                 el_confirm_seat = driver.find_element(By.ID, 'submitSeat')
#                 if el_confirm_seat is not None:
#                     try:
#                         el_confirm_seat.click()
#                     except Exception as exc:
#                         #print("click area button fail")
#                         pass
#             except Exception as exc:
#                 print("find submitSeat fail")
# '''

def tixcraft_ticket_agree(driver):
    click_plan = "A"
    #click_plan = "B"

    # check agree
    form_checkbox = None
    if click_plan == "A":
        try:
            form_checkbox = driver.find_element(By.ID, 'TicketForm_agree')
        except Exception as exc:
            print("find TicketForm_agree fail")

    is_finish_checkbox_click = False
    if form_checkbox is not None:
        try:
            # TODO: check the status: checked.
            if form_checkbox.is_enabled():
                if not form_checkbox.is_selected():
                    form_checkbox.click()
                is_finish_checkbox_click = True
        except Exception as exc:
            print("click TicketForm_agree fail")
            pass

    # 使用 plan B.
    #if not is_finish_checkbox_click:
    # alway not use Plan B.
    if False:
        try:
            print("use plan_b to check TicketForm_agree.")
            driver.execute_script("$(\"input[type='checkbox']\").prop('checked', true);")
            #driver.execute_script("document.getElementById(\"TicketForm_agree\").checked;")
            is_finish_checkbox_click = True
        except Exception as exc:
            print("javascript check TicketForm_agree fail")
            print(exc)
            pass

    return is_finish_checkbox_click

def tixcraft_ticket_number_auto_fill(driver, select_obj, ticket_number):
    is_ticket_number_assigned = False
    if select_obj is not None:
        try:
            # target ticket number
            select_obj.select_by_visible_text(ticket_number)
            #select.select_by_value(ticket_number)
            #select.select_by_index(int(ticket_number))
            is_ticket_number_assigned = True
        except Exception as exc:
            print("select_by_visible_text ticket_number fail")
            print(exc)

            try:
                # target ticket number
                select_obj.select_by_visible_text(ticket_number)
                #select.select_by_value(ticket_number)
                #select.select_by_index(int(ticket_number))
                is_ticket_number_assigned = True
            except Exception as exc:
                print("select_by_visible_text ticket_number fail...2")
                print(exc)

                # try buy one ticket
                try:
                    select_obj.select_by_visible_text("1")
                    #select.select_by_value("1")
                    #select.select_by_index(int(ticket_number))
                    is_ticket_number_assigned = True
                except Exception as exc:
                    print("select_by_visible_text 1 fail")
                    pass

    # Plan B.
    # if not is_ticket_number_assigned:
    if False:
        if select is not None:
            try:
                # target ticket number
                #select.select_by_visible_text(ticket_number)
                print("assign ticker number by jQuery:",ticket_number)
                driver.execute_script("$(\"input[type='select']\").val(\""+ ticket_number +"\");")
                is_ticket_number_assigned = True
            except Exception as exc:
                print("jQuery select_by_visible_text ticket_number fail (after click.)")
                print(exc)

    return is_ticket_number_assigned

def tixcraft_verify(driver, presale_code):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False

    inferred_answer_string = None
    if len(presale_code) > 0:
        inferred_answer_string = presale_code

    form_select = None
    try:
        form_select = driver.find_element(By.CSS_SELECTOR, '.zone-verify')
    except Exception as exc:
        print("find verify textbox fail")
        pass

    question_text = None
    if form_select is not None:
        try:
            question_text = form_select.text
        except Exception as exc:
            print("get text fail")

    html_text = ""
    if question_text is not None:
        if len(question_text) > 0:
            # format question text.
            html_text = question_text
            html_text = html_text.replace(u'「',u'【')
            html_text = html_text.replace(u'〔',u'【')
            html_text = html_text.replace(u'［',u'【')
            html_text = html_text.replace(u'〖',u'【')
            html_text = html_text.replace(u'[',u'【')

            html_text = html_text.replace(u'」',u'】')
            html_text = html_text.replace(u'〕',u'】')
            html_text = html_text.replace(u'］',u'】')
            html_text = html_text.replace(u'〗',u'】')
            html_text = html_text.replace(u']',u'】')

            if u'【' in html_text and u'】' in html_text:
                # PS: 這個太容易沖突，因為問題類型太多，不能直接使用。
                #inferred_answer_string = find_between(html_text, u"【", u"】")
                pass

    if show_debug_message:
        print("html_text:", html_text)

    is_options_in_question = False

    # 請輸入"YES"，代表您已詳閱且瞭解並同意。
    if inferred_answer_string is None:
        if u'輸入"YES"' in html_text:
            if u'已詳閱' in html_text or '請詳閱' in html_text:
                if u'同意' in html_text:
                    inferred_answer_string = 'YES'

    # 購票前請詳閱注意事項，並於驗證碼欄位輸入【同意】繼續購票流程。
    if inferred_answer_string is None:
        if '驗證碼' in html_text or '驗證欄位' in html_text:
            if '已詳閱' in html_text or '請詳閱' in html_text:
                if '輸入【同意】' in html_text:
                    inferred_answer_string = '同意'

    if show_debug_message:
        print("inferred_answer_string:", inferred_answer_string)


    form_input = None
    try:
        form_input = driver.find_element(By.CSS_SELECTOR, '#checkCode')
    except Exception as exc:
        print("find verify code fail")
        pass

    default_value = None
    if form_input is not None:
        try:
            default_value = form_input.get_attribute('value')
        except Exception as exc:
            print("find verify code fail")
            pass

    if default_value is None:
        default_value = ""

    if not inferred_answer_string is None:
        is_password_sent = False
        if len(default_value)==0:
            try:
                # PS: sometime may send key twice...
                form_input.clear()
                form_input.send_keys(inferred_answer_string)
                is_password_sent = True
                if show_debug_message:
                    print("sent password by bot.")
            except Exception as exc:
                pass

        if default_value == inferred_answer_string:
            if show_debug_message:
                print("sent password by previous time.")
            is_password_sent = True

        if is_password_sent:
            submit_btn = None
            try:
                submit_btn = driver.find_element(By.ID, 'submitButton')
            except Exception as exc:
                if show_debug_message:
                    print("find submit button fail")
                    print(exc)
                pass

            is_submited = False
            if not submit_btn is None:
                for i in range(3):
                    try:
                        if submit_btn.is_enabled():
                            submit_btn.click()
                            is_submited = True
                            if show_debug_message:
                                print("press submit button at time #", i+1)
                    except Exception as exc:
                        pass

                    if is_submited:
                        break

            if is_submited:
                for i in range(3):
                    time.sleep(0.1)
                    alert_ret = check_pop_alert(driver)
                    if alert_ret:
                        if show_debug_message:
                            print("press accept button at time #", i+1)                    
                        break
    else:
        if len(default_value)==0:
            try:
                form_input.click()
            except Exception as exc:
                pass

    return ret

def tixcraft_change_captcha(driver,url):
    try:
        driver.execute_script(f"document.querySelector('.verify-img').children[0].setAttribute('src','{url}');")
    except Exception as exc:
        print("edit captcha element fail")

def tixcraft_toast(driver, message):
    toast_element = None
    try:
        my_css_selector = ".remark-word"
        toast_element = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if not toast_element is None:
            driver.execute_script("arguments[0].innerHTML='%s';" % message, toast_element)
    except Exception as exc:
        print("find toast element fail")

def  tixcraft_keyin_captcha_code(driver, answer = "", auto_submit = False):
    is_verifyCode_editing = False
    is_form_sumbited = False

    # manually keyin verify code.
    # start to input verify code.
    form_verifyCode = None
    try:
        form_verifyCode = driver.find_element(By.ID, 'TicketForm_verifyCode')
    except Exception as exc:
        print("find form_verifyCode fail")

    if form_verifyCode is not None:
        is_visible = False
        try:
            if form_verifyCode.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            try:
                form_verifyCode.click()
                is_verifyCode_editing = True
            except Exception as exc:
                print("click form_verifyCode fail, tring to use javascript.")
                # plan B
                try:
                    driver.execute_script("document.getElementById(\"TicketForm_verifyCode\").focus();")
                    is_verifyCode_editing = True
                except Exception as exc:
                    print("click form_verifyCode fail.")

            #print("start to fill answer.")
            try:
                if len(answer) > 0:
                    form_verifyCode.send_keys(answer)
                if auto_submit:
                    form_verifyCode.send_keys(Keys.ENTER)
                    is_verifyCode_editing = False
                    is_form_sumbited = True
                else:
                    driver.execute_script("document.getElementById(\"TicketForm_verifyCode\").select();")
                    if len(answer) > 0:
                        tixcraft_toast(driver, "※ 按 Enter 如果答案是: " + answer)
            except Exception as exc:
                print("send_keys ocr answer fail.")

    return is_verifyCode_editing, is_form_sumbited

# def tixcraft_reload_captcha(driver):
#     # manually keyin verify code.
#     # start to input verify code.
#     ret = False
#     form_captcha = None
#     try:
#         form_captcha = driver.find_element(By.ID, 'yw0')
#         if not form_captcha is None:
#             form_captcha.click()
#             ret = True
#     except Exception as exc:
#         print("find form_captcha fail")

#     return ret

#PS: credit to LinShihJhang's share
# def tixcraft_auto_ocr(driver, ocr, ocr_captcha_with_submit, ocr_captcha_force_submit, previous_answer):
#     print("start to ddddocr")
#     from NonBrowser import NonBrowser

#     is_need_redo_ocr = False
#     is_form_sumbited = False

#     orc_answer = None
#     if not ocr is None:
#         Non_Browser = NonBrowser()
#         Non_Browser.Set_cookies(driver.get_cookies())
#         img_base64 = base64.b64decode(Non_Browser.Request_Captcha())
#         try:
#             orc_answer = ocr.classification(img_base64)
#         except Exception as exc:
#             pass
#     else:
#         print("ddddocr is None")
        
#     if not orc_answer is None:
#         orc_answer = orc_answer.strip()
#         print("orc_answer:", orc_answer)
#         if len(orc_answer)==4:
#             who_care_var, is_form_sumbited = tixcraft_keyin_captcha_code(driver, answer = orc_answer, auto_submit = ocr_captcha_with_submit)
#         else:
#             if not ocr_captcha_force_submit:
#                 tixcraft_keyin_captcha_code(driver)
#                 tixcraft_toast(driver, "※ Ocr fail...")
#             else:
#                 is_need_redo_ocr = True
#                 if previous_answer != orc_answer:
#                     previous_answer = orc_answer
#                     print("click captcha again")
#                     tixcraft_reload_captcha(driver)
#                     time.sleep(0.3)
#     else:
#         print("orc_answer is None")
#         print("previous_answer:", previous_answer)
#         if previous_answer is None:
#             tixcraft_keyin_captcha_code(driver)
#         else:
#             # page is not ready, retry again.
#             is_need_redo_ocr = True

#     return is_need_redo_ocr, previous_answer, is_form_sumbited

def tixcraft_ticket_main(driver, config_dict, ocr):
    auto_check_agree = config_dict["auto_check_agree"]
    
    ocr_captcha_enable = config_dict["ocr_captcha"]["enable"]
    ocr_captcha_with_submit = config_dict["ocr_captcha"]["auto_submit"]
    ocr_captcha_force_submit = config_dict["ocr_captcha"]["force_submit"]

    if auto_check_agree:
        tixcraft_ticket_agree(driver)

    # allow agree not enable to assign ticket number.
    form_select = None
    try:
        #form_select = driver.find_element(By.TAG_NAME, 'select')
        #PS: select box may appear many in the page with different price.
        form_select = driver.find_element(By.CSS_SELECTOR, '.mobile-select')
    except Exception as exc:
        print("find select fail")
        pass

    select_obj = None
    if form_select is not None:
        is_visible = False
        try:
            if form_select.is_enabled():
                is_visible = True
        except Exception as exc:
            pass
        if is_visible:
            try:
                select_obj = Select(form_select)
            except Exception as exc:
                pass

    is_ticket_number_assigned = False
    if not select_obj is None:
        row_text = None
        try:
            row_text = select_obj.first_selected_option.text
        except Exception as exc:
            pass
        if not row_text is None:
            if len(row_text) > 0:
                if row_text != "0":
                    # ticket assign.
                    is_ticket_number_assigned = True

    is_verifyCode_editing = False

    # must wait select object ready to assign ticket number.
    if not is_ticket_number_assigned:
        # only this case:"ticket number changed by bot" to play sound!
        # PS: I assume each time assign ticket number will succufully changed, so let sound play first.
        # check_and_play_sound_for_captcha(config_dict)

        ticket_number = str(config_dict["ticket_number"])
        is_ticket_number_assigned = tixcraft_ticket_number_auto_fill(driver, select_obj, ticket_number)

        # must wait ticket number assign to focus captcha.
        # if is_ticket_number_assigned:
        #     if not ocr_captcha_enable:
        #         is_verifyCode_editing =  tixcraft_keyin_captcha_code(driver)
            # else:
            #     previous_answer = None
            #     is_verifyCode_editing = True
            #     for redo_ocr in range(999):
            #         is_need_redo_ocr, previous_answer, is_form_sumbited = tixcraft_auto_ocr(driver, ocr, ocr_captcha_with_submit, ocr_captcha_force_submit, previous_answer)
            #         if is_form_sumbited:
            #             # start next loop.
            #             is_verifyCode_editing = False
            #             break
            #         if not ocr_captcha_force_submit:
            #             break
            #         if not is_need_redo_ocr:
            #             break

    if is_verifyCode_editing:
        print("goto is_verifyCode_editing == True")

    return is_verifyCode_editing


def facebook_login(driver, account):
    ret = False
    el_email = None
    try:
        el_email = driver.find_element(By.CSS_SELECTOR, '#email')
    except Exception as exc:
        pass

    is_visible = False
    if el_email is not None:
        try:
            if el_email.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    is_email_sent = False
    if is_visible:
        try:
            inputed_text = el_email.get_attribute('value')
            if inputed_text is not None:
                if len(inputed_text) == 0:
                    el_email.send_keys(account)
                    is_email_sent = True
        except Exception as exc:
            pass

    el_pass = None
    if is_email_sent:
        try:
            el_pass = driver.find_element(By.CSS_SELECTOR, '#pass')
        except Exception as exc:
            pass

    is_visible = False
    if el_pass is not None:
        try:
            if el_pass.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    if is_visible:
        try:
            el_pass.click()
        except Exception as exc:
            pass

    return ret

# def check_and_play_sound_for_captcha(config_dict):
#     play_captcha_sound = config_dict["advanced"]["play_captcha_sound"]["enable"]
#     captcha_sound_filename = config_dict["advanced"]["play_captcha_sound"]["filename"].strip()
#     if play_captcha_sound:
#         app_root = get_app_root()
#         captcha_sound_filename = os.path.join(app_root, captcha_sound_filename)
#         play_mp3_async(captcha_sound_filename)

# def play_mp3_async(sound_filename):
#     import threading
#     threading.Thread(target=play_mp3, args=(sound_filename,), daemon=True).start()

# def play_mp3(sound_filename):
#     from playsound import playsound
#     try:
#         playsound(sound_filename)
#     except Exception as exc:
#         msg=str(exc)
#         print("play sound exeption:", msg)
#         if platform.system() == 'Windows':
#             import winsound
#             try:
#                 winsound.PlaySound(sound_filename, winsound.SND_FILENAME)
#             except Exception as exc2:
#                 pass

# purpose: check alert poped.
# PS: current version not enable...
def check_pop_alert(driver):
    is_alert_popup = False

    # https://stackoverflow.com/questions/57481723/is-there-a-change-in-the-handling-of-unhandled-alert-in-chromedriver-and-chrome
    default_close_alert_text = [""]
    if len(default_close_alert_text) > 0:
        try:
            alert = None
            if not driver is None:
                alert = driver.switch_to.alert
            if not alert is None:
                alert_text = str(alert.text)
                if not alert_text is None:
                    is_match_auto_close_text = False
                    for txt in default_close_alert_text:
                        if len(txt) > 0:
                            if txt in alert.text:
                                is_match_auto_close_text = True
                        else:
                            is_match_auto_close_text = True
                    #print("is_match_auto_close_text:", is_match_auto_close_text)
                    #print("alert3 text:", alert.text)

                    if is_match_auto_close_text:
                        alert.accept()
                        print("alert3 accepted")

                    is_alert_popup = True
            else:
                print("alert3 not detected")
        except NoAlertPresentException as exc1:
            #logger.error('NoAlertPresentException for alert')
            pass
        except NoSuchWindowException:
            pass
        except Exception as exc:
            logger.error('Exception2 for alert')
            logger.error(exc, exc_info=True)

    return is_alert_popup

def list_all_cookies(driver):
    all_cookies=driver.get_cookies();
    cookies_dict = {}
    for cookie in all_cookies:
        cookies_dict[cookie['name']] = cookie['value']
    print(cookies_dict)

def tixcraft_main(driver, url, config_dict, is_verifyCode_editing):
    # if url == 'https://tixcraft.com/':
    #     tixcraft_home(driver)
    if 'https://tixcraft.com/' in url:
        tixcraft_home(driver)

    if "/activity/detail/" in url:
        is_redirected = tixcraft_redirect(driver, url)

    if "/activity/game/" in url:
        date_auto_select_enable = config_dict["tixcraft"]["date_auto_select"]["enable"]
        if date_auto_select_enable:
            tixcraft_date_auto_select(driver, url, config_dict)

    # choose area
    if '/ticket/area/' in url:
        area_auto_select_enable = config_dict["tixcraft"]["area_auto_select"]["enable"]
        if area_auto_select_enable:
            # Replace the old function call
            tixcraft_area_auto_select(driver, url, config_dict)
            print("success")

    if '/ticket/verify/' in url:
        presale_code = config_dict["tixcraft"]["presale_code"]
        tixcraft_verify(driver, presale_code)

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

    # internal variable. 說明：這是一個內部變數，請略過。
    url = ""
    last_url = ""

    # for tixcraft
    is_verifyCode_editing = False

    DISCONNECTED_MSG = 'Unable to evaluate script: no such window: target window already closed'

    debugMode = False
    if 'debug' in config_dict:
        debugMode = config_dict["debug"]
    if debugMode:
        print("Start to looping, detect browser url...")

    # ocr = None
    # try:
    #     if config_dict["ocr_captcha"]["enable"]:
    #         # ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
    #         ocr = ddddocr.DdddOcr()
    # except Exception as exc:
    #     pass
    i = 0
    while True:
        # time.sleep(0.1)

        # is_alert_popup = False

        # pass if driver not loaded.
        # if driver is None:
        #     print("web driver not accessible!")
        #     break

        #is_alert_popup = check_pop_alert(driver)

        #MUST "do nothing: if alert popup.
        #print("is_alert_popup:", is_alert_popup)
        # if is_alert_popup:
        #     continue

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

        # if url is None:
        #     continue
        # else:
        #     if len(url) == 0:
        #         continue

        # # 說明：輸出目前網址，覺得吵的話，請註解掉這行。
        # if debugMode:
        #     print("url:", url)

        # if len(url) > 0 :
        #     if url != last_url:
        #         print(url)
        #     last_url = url

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

        # for facebook
        # facebook_login_url = 'https://www.facebook.com/login.php?'
        # if url[:len(facebook_login_url)]==facebook_login_url:
        #     facebook_account = config_dict["advanced"]["facebook_account"].strip()
        #     if len(facebook_account) > 4:
        #         facebook_login(driver, facebook_account)

if __name__ == "__main__":
    # CONST_MODE_GUI = 0
    # CONST_MODE_CLI = 1
    # mode = CONST_MODE_GUI
    #mode = CONST_MODE_CLI
    
    main()


