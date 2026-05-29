import requests
import json
import base64
from PIL import Image
from io import BytesIO
import time

class NonBrowser:
    def __init__(self) -> None:
        self.Session = requests.session()
        self.url = "https://tixcraft.com/ticket/captcha"
        self.refresh_url = "https://tixcraft.com/ticket/captcha?refresh=1"

    def Set_cookies(self, cookies: list[dict]) -> bool:
        """設置 cookies 到會話中。"""
        for cookie in cookies:
            self.Session.cookies.set(cookie["name"], cookie["value"])
        return True

    def set_headers(self, headers: dict):
        """設置 HTTP 標頭。"""
        self.Session.headers.update(headers)

    def Request_Captcha(self) -> str:
        """請求驗證碼圖片，並返回 Base64 編碼的 JPEG 圖片資料。"""
        try:
            response = self.Session.get(self.url, stream=True)
            response.raise_for_status()  # 檢查是否有請求錯誤

            img = Image.open(BytesIO(response.content))  # 讀取圖片
            output_buffer = BytesIO()
            # img.save("captcha_image.png", format='PNG')  # 轉換為 PNG 格式
            img.save(output_buffer, format='PNG')  # 轉換為 PNG 格式
            binary_data = output_buffer.getvalue()

            # 將圖片轉為 Base64 字串並加上 MIME 標頭
            base64_data = base64.b64encode(binary_data).decode('utf-8')
            return base64_data
        except Exception as e:
            print(f"Request_Captcha failed: {e}")
            return ""

    def Request_Refresh_Captcha(self) -> str:
        """刷新驗證碼並返回新圖片的 URL。"""
        try:
            result = self.Session.get(self.refresh_url, stream=True)
            result.raise_for_status()  # 檢查是否有請求錯誤

            json_data = json.loads(result.text)
            return json_data.get("url", "")
        except Exception as e:
            print(f"Request_Refresh_Captcha failed: {e}")
            return ""