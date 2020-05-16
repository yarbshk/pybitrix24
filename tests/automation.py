import time
from datetime import datetime

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pybitrix24.bitrix24 import get_error_if_present

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


class TokenRefresher:
    def __init__(self, user_login, user_password, scope=''):
        self.user_login = user_login
        self.user_password = user_password
        self.tokens_updated_at = None
        self.access_token = None
        self.refresh_token = None
        self.scope = scope

    def update_tokens(self, bx24):
        if self.access_token is None or self.refresh_token is None or \
                self.are_tokens_expire():
            data = bx24.obtain_tokens(self.obtain_auth_code(bx24),
                                      scope=self.scope)
            error = get_error_if_present(data)  # TODO: Call internal method
            if error is not None:
                raise ValueError("Can't obtain tokens. " + error)

            self.tokens_updated_at = datetime.now()
            self.access_token = bx24._access_token
            self.refresh_token = bx24._refresh_token
        else:
            bx24._access_token = self.access_token
            bx24._refresh_token = self.refresh_token

    def are_tokens_expire(self):
        return self.tokens_updated_at is not None and \
            (datetime.now() - self.tokens_updated_at).seconds > 60 * 50

    def obtain_auth_code(self, bx24):
        with UnsafeAuthCodeProvider(bx24) as provider:
            return provider.request_auth_code(self.user_login,
                                              self.user_password)
