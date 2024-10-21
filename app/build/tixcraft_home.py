from selenium.webdriver.common.by import By

def tixcraft_home(driver):
    """處理首頁的彈窗與 cookies 允許提示。"""
    print("一日遊")  # Debug message

    # 點擊接受 Cookies 的按鈕
    try:
        accept_all_cookies_btn = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
        if accept_all_cookies_btn.is_enabled() and accept_all_cookies_btn.is_displayed():
            accept_all_cookies_btn.click()
    except Exception as exc:
        print("Failed to click the accept cookies button:", exc)

    # 關閉所有的彈出警告視窗
    try:
        close_all_alert_btns = driver.find_elements(By.CSS_SELECTOR, "[class='close-alert']")
        for alert_btn in close_all_alert_btns:
            if alert_btn.is_enabled() and alert_btn.is_displayed():
                alert_btn.click()
    except Exception as exc:
        print("Failed to close alert buttons:", exc)
