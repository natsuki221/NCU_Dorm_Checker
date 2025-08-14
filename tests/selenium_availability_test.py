import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException


def test_chrome_driver():
    """
    Tests specific Chrome driver functionality
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("chrome://version")
        print("Chrome driver navigation test successful")
        return True
    except Exception as e:
        print(f"Chrome driver test failed: {e}", file=sys.stderr)
        return False
    finally:
        if "driver" in locals():
            driver.quit()


def test_selenium_availability():
    """
    Tests if Selenium WebDriver can be initialized successfully.
    This checks if both the selenium library and the browser driver (e.g., chromedriver) are set up correctly.
    """
    print("Attempting to initialize Selenium WebDriver for Chrome...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("Selenium WebDriver for Chrome initialized successfully!")
        browser_version = driver.capabilities.get("browserVersion", "N/A")
        driver_version = (
            driver.capabilities.get("chrome", {})
            .get("chromedriverVersion", "N/A")
            .split(" ")[0]
        )
        print(f"Browser version: {browser_version}")
        print(f"ChromeDriver version: {driver_version}")

        # Add Chrome driver specific test
        if not test_chrome_driver():
            print("Chrome driver functionality test failed", file=sys.stderr)
            return False

        return True
    except WebDriverException as e:
        print("\nSelenium availability test FAILED.", file=sys.stderr)
        print("Could not initialize Selenium WebDriver.", file=sys.stderr)
        print("Please ensure that:", file=sys.stderr)
        print("1. You have Google Chrome installed.", file=sys.stderr)
        print(
            "2. The version of chromedriver matches your Google Chrome version.",
            file=sys.stderr,
        )
        print(
            "   (Selenium Manager usually handles this automatically, but a mismatch can still occur).",
            file=sys.stderr,
        )
        print(f"\nError details: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return False
    finally:
        if driver:
            driver.quit()
            print("WebDriver session closed.")


if __name__ == "__main__":
    if test_selenium_availability():
        print("\nSelenium is available and configured correctly.")
    else:
        print(
            "\nSelenium is not available or configured correctly. Please check the error messages above."
        )
