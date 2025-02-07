# selenium 4.28.0 on python 3.10
import time
from selenium import webdriver

def create_webdriver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)

    return driver

if __name__ == "__main__":
    driver = create_webdriver()
    driver.get('http://www.google.com')
    time.sleep(10)
    print(driver.title)
    # driver.quit()