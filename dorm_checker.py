import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv

# 可選：2Captcha 整合（需安裝 twocaptcha 模組：pip install twocaptcha）
# from twocaptcha import TwoCaptcha

load_dotenv()

# 設定變數
username = os.getenv("USERNAME", "您的帳號")
password = os.getenv("PASSWORD", "您的密碼")
discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "您的Discord Webhook URL")
dorm_name = ["DormGH_1", "DormGH_2", "DormHsiW_1", "DormHsiW_2"]
# 可選：2Captcha API Key
# twocaptcha_api_key = os.getenv("TWOCAPTCHA_API_KEY", "您的2Captcha API Key")

# 登入與查詢URL
login_url = "https://portal.ncu.edu.tw/login"
query_url = "https://cis.ncu.edu.tw/iNCU/stdAffair/dormEmptyBedSearch"

# 定義要設置的headers
custom_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Dnt": "1",
    "Priority": "u=0, i",
    "Sec-Ch-Ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:131.0) Gecko/20100101 Firefox/131.0",
}


# Discord通知函數
def send_discord_notification(message):
    """發送Discord通知"""
    payload = {"content": message}
    requests.post(discord_webhook_url, json=payload)


# 檢查宿舍空房函數
def check_is_dorm_empty(driver, dorm_name, wait):
    """檢查指定宿舍是否有空房"""
    try:
        # 選擇宿舍下拉選單
        dorm_select = Select(driver.find_element(By.ID, "buliding_no"))
        dorm_select.select_by_value(dorm_name)

        # 送出查詢表單
        submit_button = driver.find_element(
            By.XPATH, "/html/body/div[4]/div/form/table/tbody/tr[3]/th/input"
        )
        submit_button.click()

        time.sleep(2)  # 等待頁面載入

        # 等待結果載入
        wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div[4]/div/table | /html/body/div[4]/div/div[3]/p",
                )
            )
        )

        # 檢查是否有空房
        try:
            result_table = driver.find_element(By.XPATH, "/html/body/div[4]/div/table")
            rows = result_table.find_elements(By.XPATH, ".//tbody/tr")
            if len(rows) > 1:  # 假設第一行是標頭，若有更多行表示有空房
                message = f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] 宿舍 {dorm_name} 有空房！請盡快查詢：{query_url}'
                send_discord_notification(message)
                print(message)
            else:
                print(
                    f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] 宿舍 {dorm_name} 目前無空房。'
                )
        except:
            # 若找不到表格，檢查無空房提示訊息
            driver.find_element(By.XPATH, "/html/body/div[4]/div/div[3]/p")
            print(
                f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] 宿舍 {dorm_name} 目前無空房。'
            )

    except Exception as e:
        print(f"檢查宿舍 {dorm_name} 時發生錯誤：{str(e)}")


# 主檢查函數
def check_dorm_availability():
    """執行單次檢查"""
    firefox_options = Options()
    # 移除 --headless 以觀察 reCAPTCHA
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument(
        f'--user-agent={custom_headers["User-Agent"]}'
    )  # 設置User-Agent
    firefox_options.add_argument("--lang=zh-TW")  # 設置語言
    firefox_options.add_argument("--disable-notifications")  # 禁用通知

    # 使用 Firefox Profile 設置部分 headers
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.http.accept", custom_headers["Accept"])
    profile.set_preference(
        "network.http.accept-encoding", custom_headers["Accept-Encoding"]
    )
    profile.set_preference(
        "network.http.accept-language", custom_headers["Accept-Language"]
    )
    profile.set_preference(
        "network.http.upgrade-insecure-requests",
        int(custom_headers["Upgrade-Insecure-Requests"]),
    )
    firefox_options.profile = profile

    driver = webdriver.Firefox(options=firefox_options)

    try:
        # 隱藏 navigator.webdriver
        driver.execute_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
        )

        # 步驟1: 登入
        driver.get(login_url)
        wait = WebDriverWait(driver, 5)

        # 檢查是否有Cookie提示並接受
        try:
            cookie_button = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(text(), '接受') or contains(text(), 'Accept')]",
                    )
                )
            )
            cookie_button.click()
            print("已接受Cookie提示。")
        except:
            print("未偵測到Cookie提示。")

        # 輸入帳號
        username_input = wait.until(
            EC.presence_of_element_located((By.ID, "inputAccount"))
        )
        username_input.send_keys(username)

        # 模擬人類行為：隨機滑鼠移動
        ActionChains(driver).move_to_element(username_input).move_by_offset(
            random.randint(-50, 50), random.randint(-50, 50)
        ).perform()

        # 輸入密碼
        password_input = driver.find_element(By.ID, "inputPassword")
        password_input.send_keys(password)

        # 模擬人類行為：隨機延遲
        time.sleep(random.uniform(0.5, 2))

        # 處理reCAPTCHA（手動介入）
        try:
            recaptcha_element = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='g-recaptcha']")
                )
            )
            print("偵測到reCAPTCHA，請在10秒內手動完成驗證...")
            time.sleep(10)  # 等待15秒讓使用者手動完成reCAPTCHA
        except:
            print("未檢測到reCAPTCHA，或已自動通過。")

        # 提交登入
        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_button.click()

        # 等待登入成功
        wait.until(EC.url_contains("portal.ncu.edu.tw/my/"))

        # 步驟2: 導航到查詢頁面
        driver.get(query_url)
        time.sleep(random.uniform(1, 2))  # 等待頁面載入

        # 步驟3: 處理跳轉頁面
        try:
            proceed_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), '前往')]")
                )
            )
            proceed_button.click()
            print("已點擊跳轉頁面的「前往」按鈕。")
        except:
            print("未偵測到跳轉頁面或「前往」按鈕，直接嘗試進入查詢頁面。")

        # 等待頁面載入
        wait.until(EC.presence_of_element_located((By.ID, "formEmptyBed")))

        # 步驟4: 檢查每個宿舍
        for i in range(random.randint(7, 10)):
            for dorm in dorm_name:
                time.sleep(random.uniform(1, 3))
                check_is_dorm_empty(driver, dorm, wait)
                # 返回查詢頁面以進行下一次查詢
                time.sleep(random.uniform(1, 2))
                # driver.get(query_url)
                wait.until(EC.presence_of_element_located((By.ID, "formEmptyBed")))

            print(f"第 {i + 1} 次檢查完成，等待下一次檢查...")

    except Exception as e:
        print(f"錯誤發生：{str(e)}，將在下次間隔重試。")
        if "Cookie unaccepted" in str(e):
            driver.delete_all_cookies()
            print("已清除Cookie，將重試。")

    finally:
        driver.quit()


# 主迴圈：定時執行
if __name__ == "__main__":
    send_discord_notification("歡迎使用：NCU宿舍空房檢查系統")
    send_discord_notification(
        "啟用時間：{ " + time.strftime("%Y-%m-%d %H:%M:%S") + " }"
    )
    while True:
        check_dorm_availability()
        interval = random.randint(480, 600)  # 8~10分鐘隨機秒數
        print(f"等待 {interval} 秒後下次檢查...")
        time.sleep(interval)
