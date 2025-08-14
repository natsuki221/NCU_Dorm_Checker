import os
import time
import random
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv

# 可選：2Captcha 整合（需安裝 twocaptcha 模組：pip install twocaptcha）
# from twocaptcha import TwoCaptcha

load_dotenv()

# 設定變數
username = os.getenv("USERNAME", "您的帳號")
password = os.getenv("PASSWORD", "您的密碼")
# 可選：2Captcha API Key
# twocaptcha_api_key = os.getenv("TWOCAPTCHA_API_KEY", "您的2Captcha API Key")

# 登入URL
login_url = "https://portal.ncu.edu.tw/login"

# 定義要設置的headers
custom_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Dnt": "1",
    "Priority": "u=0, i",
    "Sec-Ch-Ua": '"Chromium";v="139", "Not;A=Brand";v="99"',  # Firefox 會忽略部分Sec- headers
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:131.0) Gecko/20100101 Firefox/131.0",
}

def test_login():
    """測試NCU Portal登入（使用Firefox）"""
    firefox_options = Options()
    # 移除 --headless 以觀察 reCAPTCHA
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument(f'--user-agent={custom_headers["User-Agent"]}')  # 設置User-Agent
    firefox_options.add_argument("--lang=zh-TW")  # 設置語言
    firefox_options.add_argument("--disable-notifications")  # 禁用通知

    # 使用 Firefox Profile 設置部分 headers
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.http.accept", custom_headers["Accept"])
    profile.set_preference("network.http.accept-encoding", custom_headers["Accept-Encoding"])
    profile.set_preference("network.http.accept-language", custom_headers["Accept-Language"])
    profile.set_preference("network.http.upgrade-insecure-requests", int(custom_headers["Upgrade-Insecure-Requests"]))
    firefox_options.profile = profile

    driver = webdriver.Firefox(options=firefox_options)

    try:
        # 隱藏 navigator.webdriver
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)

        # 步驟1: 開啟登入頁面
        driver.get(login_url)
        wait = WebDriverWait(driver, 5)  # 延長等待時間

        # 檢查是否有Cookie提示並接受
        try:
            cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '接受') or contains(text(), 'Accept')]")))
            cookie_button.click()
            print("已接受Cookie提示。")
        except:
            print("未偵測到Cookie提示。")

        # 步驟2: 輸入帳號
        username_input = wait.until(EC.presence_of_element_located((By.ID, "inputAccount")))
        username_input.send_keys(username)

        # 模擬人類行為：隨機滑鼠移動
        ActionChains(driver).move_to_element(username_input).move_by_offset(random.randint(-50, 50), random.randint(-50, 50)).perform()

        # 步驟3: 輸入密碼
        password_input = driver.find_element(By.ID, "inputPassword")
        password_input.send_keys(password)

        # 模擬人類行為：隨機延遲
        time.sleep(random.uniform(0.5, 2))

        # 步驟4: 處理reCAPTCHA（手動介入）
        try:
            recaptcha_element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='g-recaptcha']")))
            print("偵測到reCAPTCHA，請在15秒內手動完成驗證...")
            time.sleep(15)  # 延長等待時間，讓使用者完成驗證

            # 可選：2Captcha 自動解決（需取消註解並配置）
            """
            solver = TwoCaptcha(twocaptcha_api_key)
            recaptcha_response = solver.recaptcha(sitekey='網站的reCAPTCHA site key', url=login_url)
            driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML="{recaptcha_response["code"]}";')
            print("reCAPTCHA 已由2Captcha自動解決。")
            """
        except:
            print("未偵測到reCAPTCHA，或頁面載入失敗。")

        # 步驟5: 提交登入
        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_button.click()

        # 步驟6: 等待登入結果
        wait.until(EC.url_contains("portal.ncu.edu.tw/my/"))  # 檢查是否導向成功頁面

        # 登入成功
        print("登入測試成功！目前URL:", driver.current_url)
        return True

    except Exception as e:
        print("登入測試失敗！錯誤訊息:", str(e))
        if "Cookie unaccepted" in str(e):
            driver.delete_all_cookies()
            print("已清除Cookie，請重試。")
        return False

    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_login()
    if success:
        print("測試通過：登入功能正常。")
    else:
        print("測試失敗：請檢查帳號、密碼、reCAPTCHA 或網路環境。")