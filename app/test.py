import undetected_chromedriver as uc
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def main():
    # 設置 ChromeDriver 路徑
    webdriver_path = os.path.join("webdriver", "chromedriver")
    print(webdriver_path)

    # ser = Service()
    # ser.executable_path = webdriver_path	# 指定 ChromeDriver 的路径

    # # 初始化 WebDriver，使用之前创建 Service 对象
    driver = uc.Chrome()

    # 創建 Chrome 瀏覽器選項
    options = uc.ChromeOptions()
    # options.add_argument('--user-data-dir=/Users/julian/Library/Application Support/Google/Chrome')
    # options.add_argument('--profile-directory=Profile 4')


    try:
        # 創建 undetected ChromeDriver 實例
        driver = uc.Chrome(options=options, executable_path=webdriver_path)
        driver.get("https://tixcraft.com/")
        # driver.get("https://www.google.com/")
        # 驗證 driver 是否創建成功
        print("ChromeDriver 創建成功！")

        with open("cookies.txt", "r") as f:
            cookies = eval(f.read())
        for cookie in cookies:
            driver.add_cookie(cookie)
        print("重新整理")
        driver.refresh()
            
        # 等待页面加载完成
        print("成功登入")

        for i in range(1, 11):
            time.sleep(1)
            print(f"已經過了 {i} 秒")

        
        # # 获取并保存 cookies
        # cookies = driver.get_cookies()
        # with open("cookies.txt", "w") as f:
        #     f.write(str(cookies))
        # print("Cookies 已保存！")
    except Exception as e:
        # 捕獲異常並打印錯誤信息
        print("ChromeDriver 創建失敗：", e)
    
    finally:
        # 確保在成功創建 driver 時能夠關閉它
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()

# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# logger.info("测试日志输出")
