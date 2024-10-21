from selenium.webdriver.common.by import By

def facebook_login(driver, account):
    """執行 Facebook 登入流程。"""
    ret = False

    # 尋找 email 輸入框
    try:
        el_email = driver.find_element(By.CSS_SELECTOR, '#email')
        if el_email.is_enabled() and el_email.get_attribute('value') == "":
            el_email.send_keys(account)
            print("Email entered successfully.")
            is_email_sent = True
        else:
            is_email_sent = False
    except Exception as exc:
        print("Failed to enter email:", exc)
        is_email_sent = False

    # 如果 email 輸入成功，嘗試輸入密碼
    if is_email_sent:
        try:
            el_pass = driver.find_element(By.CSS_SELECTOR, '#pass')
            if el_pass.is_enabled():
                el_pass.click()
                print("Password field clicked.")
        except Exception as exc:
            print("Failed to click the password field:", exc)

    return ret
