import time

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs


def parse_query_param(param_name, url):
    parse_result = urlparse(url)
    return parse_qs(parse_result.query)[param_name][0]


class UnsafeAuthCodeProvider:
    """
    A helper class for automatic requesting authorization codes (without direct
    browser interaction). An absolute path to the executable "chromedriver"
    should be in PATH to make it work.
    """
    bitrix24_passport_url = 'https://www.bitrix24.net/'

    def __init__(self, bitrix24, headless=True):
        self.bx24 = bitrix24
        self.headless = headless
        self.driver = Chrome(options=self._provide_chrome_options())
        self.wait = WebDriverWait(self.driver, 60)

    def _provide_chrome_options(self):
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-logging"])  # disable logging
        if self.headless:
            chrome_options.add_argument('--headless')
        return chrome_options

    def __enter__(self):
        return self

    def request_auth_code(self, user_login, user_password):
        # Login to Bitrix24 Passport (provide user session)
        self.driver.get(self.bitrix24_passport_url)

        self._input_and_continue((By.ID, 'login'), user_login)
        self._input_and_continue((By.ID, 'password'), user_password)

        time.sleep(1)

        # Simulate obtaining an authorization code by a resource owner
        self.driver.get(self.bx24.build_authorization_url())
        auth_code = parse_query_param('code', self.driver.current_url)

        return auth_code

    def _input_and_continue(self, locator, text):
        element = self.wait.until(EC.presence_of_element_located(locator))
        element.send_keys(text)
        time.sleep(1)
        element.send_keys(Keys.ENTER)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()
