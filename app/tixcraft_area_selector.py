# tixcraft_area_selector.py

import random
from selenium.webdriver.common.by import By
import logging
import time

logger = logging.getLogger() 

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
    start_time = time.perf_counter()
    logger.info("开始执行 get_tixcraft_target_area")

    is_need_refresh = False
    matched_blocks = None

    area_list = None
    area_list_count = 0

    block1_start = time.perf_counter()
    if el is not None:
        try:
            area_list = el.find_elements(By.TAG_NAME, 'a')
            area_list_count = len(area_list) if area_list else 0
            logger.info(f"找到 {area_list_count} 个区域")
            if area_list_count == 0:
                print("area list is empty, do refresh!")
                is_need_refresh = True
        except Exception as exc:
            is_need_refresh = True
            pass
    else:
        print("area list is None, do refresh!")
        is_need_refresh = True
    print("area_list",area_list)
    block1_end = time.perf_counter()
    logger.info(f"代码块1(获取区域列表)耗时 {block1_end - block1_start:.4f} 秒")

    block2_start = time.perf_counter()
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
                    logger.error("获取区域文本失败", exc_info=True)
                    continue
            print("row_text", row_text)

            if row_text:
                formatted_row_text = format_keyword_string(row_text)
                formatted_area_keyword = format_keyword_string(area_keyword)
                is_append_this_row = False
                if formatted_area_keyword in formatted_row_text:
                    is_append_this_row = True

                if is_append_this_row:
                    matched_blocks.append(row)
                    logger.info(f"匹配到的区域：{row_text}")
                    # if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                    #     break

        if len(matched_blocks) == 0:
            matched_blocks = None
            is_need_refresh = True
    print("match_blocks",matched_blocks)

    block2_end = time.perf_counter()
    logger.info(f"代码块2(匹配区域)耗时 {block2_end - block2_start:.4f} 秒")

    end_time = time.perf_counter()
    total_time = end_time - start_time
    logger.info(f"get_tixcraft_target_area 总耗时 {total_time:.4f} 秒")

    return is_need_refresh, matched_blocks

def tixcraft_area_auto_select(driver, url, config_dict):
    start_time = time.perf_counter()
    logger.info("开始执行 tixcraft_area_auto_select")

    block1_start = time.perf_counter()
    area_keyword_1 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_1"].strip()
    area_auto_select_mode = config_dict["tixcraft"]["area_auto_select"]["mode"]
    pass_1_seat_remaining_enable = config_dict["pass_1_seat_remaining"]
    ticket_number = config_dict["ticket_number"]
    if ticket_number == 1:
        pass_1_seat_remaining_enable = False
    block1_end = time.perf_counter()
    logger.info(f"代码块1(初始化变量)耗时 {block1_end - block1_start:.4f} 秒")

    # 代码块2：检查 URL 是否包含 '/ticket/area/'
    block2_start = time.perf_counter()
    if '/ticket/area/' in url:
        block2_end = time.perf_counter()
        logger.info(f"代码块2(检查 URL)耗时 {block2_end - block2_start:.4f} 秒")

        block3_start = time.perf_counter()
        el = None
        try:
            el = driver.find_element(By.CSS_SELECTOR, '.zone')
        except Exception as exc:
            print("find .zone fail, do nothing.")
        block3_end = time.perf_counter()
        logger.info(f"代码块3(查找元素)耗时 {block3_end - block3_start:.4f} 秒")

        # 代码块4：获取目标区域
        block4_start = time.perf_counter()
        if el is not None:
            is_need_refresh, areas = get_tixcraft_target_area(
                el, area_keyword_1, area_auto_select_mode, pass_1_seat_remaining_enable
            )
            block4_end = time.perf_counter()
            logger.info(f"代码块4(获取目标区域)耗时 {block4_end - block4_start:.4f} 秒")

            # 代码块5：选择区域
            block5_start = time.perf_counter()
            area_target = None
            if areas is not None:
                target_row_index = 0
                # if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                #     target_row_index = len(areas) - 1
                # if area_auto_select_mode == CONST_RANDOM:
                #     target_row_index = random.randint(0, len(areas) - 1)
                area_target = areas[target_row_index]
            block5_end = time.perf_counter()
            logger.info(f"代码块5(选择区域)耗时 {block5_end - block5_start:.4f} 秒")
            
            # 代码块6：点击区域
            block6_start = time.perf_counter()
            if area_target is not None:
                # try:
                #     area_target.click()
                # except Exception as exc:
                try:
                    driver.execute_script("arguments[0].click();", area_target)
                except Exception as exc:
                    print("click area a link fail.")
            block6_end = time.perf_counter()
            logger.info(f"代码块6(点击区域)耗时 {block6_end - block6_start:.4f} 秒")
            
            if is_need_refresh:
                try:
                    driver.refresh()
                except Exception as exc:
                    pass
    end_time = time.perf_counter()
    total_time = end_time - start_time
    logger.info(f"tixcraft_area_auto_select 总耗时 {total_time:.4f} 秒")