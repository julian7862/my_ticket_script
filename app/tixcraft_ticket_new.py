from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from openai import OpenAI
import logging
import os
import time
import requests
import base64
from NonBrowser import NonBrowser


logger = logging.getLogger() 

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def tixcraft_ticket_agree_new(driver):
    block_start = time.perf_counter()
    """點選同意票券購買條款。"""
    try:
        form_checkbox = driver.find_element(By.ID, 'TicketForm_agree')
        if form_checkbox.is_enabled() and not form_checkbox.is_selected():
            # form_checkbox.click()
            print("checkbox_enable")
            driver.execute_script("arguments[0].click();", form_checkbox)
            logger.info(f"同意票券條款耗時 {time.perf_counter() - block_start:.4f} 秒") 
        return True
    except Exception as exc:
        print("Failed to click TicketForm_agree:", exc)
        return False

def tixcraft_ticket_number_auto_fill_new(driver, select_obj, ticket_number):
    block_start = time.perf_counter()
    """自動填入購票數量。"""
    try:
        select_obj.select_by_visible_text(ticket_number)
        logger.info(f"自動填入票數耗時 {time.perf_counter() - block_start:.4f} 秒")
        return True
    except Exception as exc:
        print(f"Failed to select {ticket_number} tickets:", exc)
        return False

def tixcraft_ticket_main_new(driver, config_dict):
    """購票主要流程，包括同意條款和選擇票數。"""
    block_start = time.perf_counter()
    if config_dict["auto_check_agree"]:
        tixcraft_ticket_agree_new(driver)

    block2_start = time.perf_counter()
    form_select = None
    try:
        form_select = driver.find_element(By.CSS_SELECTOR, '.mobile-select')
        select_obj = Select(form_select) if form_select.is_enabled() else None
    except Exception as exc:
        print("Failed to find or enable the ticket select box:", exc)
        select_obj = None
    logger.info(f"查找選擇票數表單耗時 {time.perf_counter() - block2_start:.4f} 秒")

        # Block 3: 確認票數是否已選定
    block3_start = time.perf_counter()
    is_ticket_number_assigned = False
    if select_obj:
        try:
            if select_obj.first_selected_option.text != "0":
                is_ticket_number_assigned = True
        except Exception as exc:
            print("Error reading selected ticket option:", exc)

    if not is_ticket_number_assigned:
        ticket_number = str(config_dict["ticket_number"])
        is_ticket_number_assigned = tixcraft_ticket_number_auto_fill_new(driver, select_obj, ticket_number)
    logger.info(f"確認票數是否選定耗時 {time.perf_counter() - block3_start:.4f} 秒")

    print("抓驗證碼圖片start")
    block4_start = time.perf_counter()

    # 截圖
    captcha_img = driver.find_element(By.ID, "TicketForm_verifyCode-image")
    captcha_img.screenshot("captcha_image.png")
    # Getting the base64 string
    base64_image = encode_image("captcha_image.png")

    # 老方法
    # Non_Browser = NonBrowser()
    # Non_Browser.Set_cookies(driver.get_cookies())
    # base64_image = Non_Browser.Request_Captcha()

    logger.info(f"抓取驗證碼圖片耗時 {time.perf_counter() - block4_start:.4f} 秒")
    print("base64_image",base64_image)

    llm_start = time.perf_counter()
    logger.info("開始 LLM 驗證碼解碼")
    client = OpenAI(
        base_url=os.environ["TRENDMICRO_API_BASE_URL"],
        api_key=os.environ["TRENDMICRO_API_KEY"],
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Just give me the four English letters of the image without space, no need other words and punctuations",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
    )

    # Extract the content of the first choice from the response
    response_text = response.choices[0].message.content
    logger.info(f"LLM 解碼完成，耗時 {time.perf_counter() - llm_start:.4f} 秒，結果為: {response_text}")
    # print(f"驗證碼為： {response_text}")
    # 找到驗證碼輸入框
    submit_start = time.perf_counter()
    captcha_input = driver.find_element(By.ID, "TicketForm_verifyCode")
    # 將驗證碼輸入到輸入框中
    captcha_input.send_keys(response_text)

    try:
        confirm_button = driver.find_element(By.CLASS_NAME, "btn-primary")
        driver.execute_script("arguments[0].click();", confirm_button)
        logger.info(f"提交驗證碼成功，耗時 {time.perf_counter() - submit_start:.4f} 秒")    
        print("按鈕已通過 JavaScript 點擊")
    except Exception as e:
        print(f"使用 JavaScript 點擊失敗: {e}")


    return is_ticket_number_assigned