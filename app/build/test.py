import undetected_chromedriver as uc
import os

def main():
    # 設置 ChromeDriver 路徑
    webdriver_path = os.path.join("webdriver", "chromedriver")
    print(webdriver_path)
    
    # 創建 Chrome 瀏覽器選項
    options = uc.ChromeOptions()
    
    try:
        # 創建 undetected ChromeDriver 實例
        driver = uc.Chrome(executable_path=webdriver_path, options=options)
        
        # 驗證 driver 是否創建成功
        print("ChromeDriver 創建成功！")
        
    except Exception as e:
        # 捕獲異常並打印錯誤信息
        print("ChromeDriver 創建失敗：", e)
    
    finally:
        # 確保在成功創建 driver 時能夠關閉它
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()