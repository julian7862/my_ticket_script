# tixcraft_date_selector.py
import random
import time
from selenium.webdriver.common.by import By

CONST_FROM_TOP_TO_BOTTOM = "from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = "from bottom to top"
CONST_RANDOM = "random"

# PS: for big events, check sold out text maybe not helpful, due to database is too busy.
SOLD_OUT_TEXT_LIST = ["\u9078\u8cfc\u4e00\u7a7a", "No tickets available", "\u7a7a\u5e2d\u306a\u3057"]
COMING_SOON_CONDITIONS_LIST = [
    '\u958b\u8ce3', '\u5269\u9918', '\u5929', '\u5c0f\u6642', '\u5206\u9418', '\u79d2', '0', ':', '/'
]

def tixcraft_date_auto_select(driver, url, config_dict):
    show_debug_message = False  # Set to True for debugging purposes

    date_auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    game_name = ""
    if "/activity/game/" in url:
        url_split = url.split("/")
        if len(url_split) >= 6:
            game_name = url_split[5]

    if show_debug_message:
        print('get date game_name:', game_name)
        print("date_auto_select_mode:", date_auto_select_mode)
        print("date_keyword:", date_keyword)

    check_game_detail = False
    if "/activity/game/%s" % (game_name,) in url:
        check_game_detail = True

    print("game_name", game_name)
    print("check_game_detail", check_game_detail)

    date_list = None
    if check_game_detail:
        try:
            # date_list = driver.find_elements(By.CSS_SELECTOR, '#gameList > table > tbody > tr')
            date_list = driver.find_elements(By.CSS_SELECTOR, 'tr.gridc.fcTxt')
        except Exception as exc:
            print("find #gameList fail")

    is_coming_soon = True
    button_list = None

    if date_list is not None:
        button_list = []
        for row in date_list:
            is_match_keyword_row = False
            row_text = ""
            try:
                row_text = row.text
            except Exception as exc:
                print("get text fail")
                break
            print("row_text:", row_text)
            if len(row_text) > 0:
                # if all(cond in row_text for cond in COMING_SOON_CONDITIONS_LIST):
                #     is_coming_soon = True
                #     break
                # if len(date_keyword) == 0 or date_keyword in row_text:
                #     is_match_keyword_row = True
                # if is_match_keyword_row and pass_date_is_sold_out_enable:
                #     for sold_out_item in SOLD_OUT_TEXT_LIST:
                #         row_text_right_part = row_text[(len(sold_out_item) + 5) * -1:]
                #         if sold_out_item in row_text_right_part:
                #             is_match_keyword_row = False
                #             if show_debug_message:
                #                 print("match sold out text: %s, skip this row." % sold_out_item)
                #             break

                try:
                    el = row.find_element(By.CSS_SELECTOR, 'button.btn-primary')
                    data_href = el.get_attribute('data-href')
                    if data_href:
                        print(f"找到的 data-href: {data_href}")
                except Exception as exc:
                    if show_debug_message:
                        print("find button.btn-primary fail")
                    el = None
                    raise
                if  data_href is not None:
                    button_list.append(data_href)
                    # if date_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                    #     break
    
    print(button_list)            
    if button_list:
        try:
            driver.get(button_list[0])
            is_coming_soon = False
        except Exception as exc:
            print("導航到訂購頁面失敗")
            pass

    if auto_reload_coming_soon_page_enable and is_coming_soon:
        try:
            driver.refresh()
            print("沒找到選區網頁 reload")
        except Exception as exc:
            pass
    else:
        print("已經切換頁面不用 reload 了")
    time.sleep(5)
    # time.sleep(10)
    # exit()
    # if button_list is not None:
    #     if len(button_list) > 0:
    #         target_row_index = 0
    #         #  現在是 "mode": "from top to bottom"
    #         if date_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
    #             target_row_index = len(button_list) - 1
    #         elif date_auto_select_mode == CONST_RANDOM:
    #             target_row_index = random.randint(0, len(button_list) - 1)

    #         if show_debug_message:
    #             print("clicking row:", target_row_index + 1)

    #         try:
    #             el = button_list[target_row_index]
    #             el.click()
    #             is_date_selected = True
    #         except Exception as exc:
    #             print("try to click .btn-next fail")
    #             try:
    #                 driver.execute_script("arguments[0].click();", el)
    #             except Exception as exc:
    #                 pass