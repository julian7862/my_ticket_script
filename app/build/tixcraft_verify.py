import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
from selenium.common.exceptions import NoSuchWindowException
import logging
logging.basicConfig()
logger = logging.getLogger('logger')

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

def tixcraft_verify(driver, presale_code):
    """驗證票券頁面的驗證碼或同意訊息。"""
    inferred_answer_string = presale_code if presale_code else None

    # 查找驗證區域的元素
    try:
        form_select = driver.find_element(By.CSS_SELECTOR, '.zone-verify')
        question_text = form_select.text if form_select else ""
    except NoSuchElementException:
        print("find verify textbox fail")
        question_text = ""

    # 格式化問題文字
    html_text = question_text.replace(u'「', u'【').replace(u'」', u'】').replace('[', '【').replace(']', '】')

    # 根據提示自動推測答案
    if inferred_answer_string is None:
        if '輸入"YES"' in html_text and '同意' in html_text:
            inferred_answer_string = 'YES'
        elif '驗證碼' in html_text and '輸入【同意】' in html_text:
            inferred_answer_string = '同意'

    print("inferred_answer_string:", inferred_answer_string)

    # 找到輸入驗證碼的欄位
    try:
        form_input = driver.find_element(By.CSS_SELECTOR, '#checkCode')
        default_value = form_input.get_attribute('value') or ""
    except NoSuchElementException:
        print("find verify code fail")
        return False

    # 自動填入驗證碼或同意文字
    if inferred_answer_string and not default_value:
        try:
            form_input.clear()
            form_input.send_keys(inferred_answer_string)
            print("sent password by bot.")
        except Exception as exc:
            print("Error sending password:", exc)

    # 提交表單
    try:
        submit_btn = driver.find_element(By.ID, 'submitButton')
        for _ in range(3):
            if submit_btn.is_enabled():
                submit_btn.click()
                print("press submit button")
                time.sleep(0.1)
                if check_pop_alert(driver):
                    print("alert accepted")
                    break
    except NoSuchElementException:
        print("find submit button fail")

    return True
