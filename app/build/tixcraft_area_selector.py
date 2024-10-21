# tixcraft_area_selector.py

import random
from selenium.webdriver.common.by import By

CONST_FROM_TOP_TO_BOTTOM = u"from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = u"from bottom to top"
CONST_RANDOM = u"random"


def format_keyword_string(keyword):
    if not keyword is None:
        if len(keyword) > 0:
            keyword = keyword.replace('／','/')
            keyword = keyword.replace(' ','')
            keyword = keyword.replace(',','')
            keyword = keyword.replace('，','')
            keyword = keyword.replace('$','')
            keyword = keyword.replace(' ','').lower()
    return keyword

def get_tixcraft_target_area(el, area_keyword, area_auto_select_mode, pass_1_seat_remaining_enable):
    # show_debug_message = True       # debug.
    # show_debug_message = False      # online

    is_need_refresh = False
    matched_blocks = None

    area_list = None
    area_list_count = 0
    if el is not None:
        try:
            area_list = el.find_elements(By.TAG_NAME, 'a')
        except Exception as exc:
            pass

        if area_list is not None:
            area_list_count = len(area_list)
            if area_list_count == 0:
                print("area list is empty, do refresh!")
                is_need_refresh = True
        else:
            print("area list is None, do refresh!")
            is_need_refresh = True
    print("area_list",area_list)

    if area_list_count > 0:
        matched_blocks = []
        for row in area_list:
            row_is_enabled = False
            try:
                row_is_enabled = row.is_enabled()
            except Exception as exc:
                pass

            row_text = ""
            if row_is_enabled:
                try:
                    row_text = row.text
                except Exception as exc:
                    print("get text fail")
                    break
            print("row_text", row_text)

            if row_text is None:
                row_text = ""

            if len(row_text) > 0:
                row_text = format_keyword_string(row_text)
                is_append_this_row = False
                if len(area_keyword) > 0:
                    area_keyword = format_keyword_string(area_keyword)
                if len(area_keyword) > 0:
                    if area_keyword in row_text:
                        is_append_this_row = True
                # else:
                #     is_append_this_row = True

                # if is_append_this_row:
                #     if pass_1_seat_remaining_enable:
                #         area_item_font_el = None
                #         try:
                #             area_item_font_el = row.find_element(By.TAG_NAME, 'font')
                #             if not area_item_font_el is None:
                #                 font_el_text = area_item_font_el.text or ""
                #                 font_el_text = "@%s@" % font_el_text
                #                 for check_item in ['@1 seat(s) remaining', '剩餘 1@', '@1 席残り']:
                #                     if check_item in font_el_text:
                #                         is_append_this_row = False
                #         except Exception as exc:
                #             pass

                if is_append_this_row:
                    matched_blocks.append(row)
                    # if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                    #     break

        if len(matched_blocks) == 0:
            matched_blocks = None
            is_need_refresh = True
    print("match_blocks",matched_blocks)

    return is_need_refresh, matched_blocks

def tixcraft_area_auto_select(driver, url, config_dict):
    area_keyword_1 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_1"].strip()
    area_auto_select_mode = config_dict["tixcraft"]["area_auto_select"]["mode"]
    pass_1_seat_remaining_enable = config_dict["pass_1_seat_remaining"]
    ticket_number = config_dict["ticket_number"]
    if ticket_number == 1:
        pass_1_seat_remaining_enable = False

    if '/ticket/area/' in url:
        el = None
        try:
            el = driver.find_element(By.CSS_SELECTOR, '.zone')
        except Exception as exc:
            print("find .zone fail, do nothing.")

        if el is not None:
            is_need_refresh, areas = get_tixcraft_target_area(
                el, area_keyword_1, area_auto_select_mode, pass_1_seat_remaining_enable
            )

            area_target = None
            if areas is not None:
                target_row_index = 0
                # if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                #     target_row_index = len(areas) - 1
                # if area_auto_select_mode == CONST_RANDOM:
                #     target_row_index = random.randint(0, len(areas) - 1)
                area_target = areas[target_row_index]

            if area_target is not None:
                try:
                    area_target.click()
                except Exception as exc:
                    try:
                        driver.execute_script("arguments[0].click();", area_target)
                    except Exception as exc:
                        print("click area a link fail.")
            
            if is_need_refresh:
                try:
                    driver.refresh()
                except Exception as exc:
                    pass
