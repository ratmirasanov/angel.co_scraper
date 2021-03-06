"""Module Utilities with different useful methods."""

import time
import datetime
import json
import re
from itertools import groupby
import requests

from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import config
import bad_sites


class Utilities:
    """Class Utilities with different useful methods."""
    URL = ""

    def fill_form(self, data, path=''):
        """A method for filling html form on the page."""

        for key, val in data.items():
            if isinstance(val) != dict:

                try:
                    element_name = key

                    try:
                        if path != '':
                            element_name = '{}__{}'.format(path, element_name)

                        element = self.find_by_id(element_name)
                    except (TimeoutException, NoSuchElementException):
                        if path != '':
                            element_name = '{}[{}]'.format(path, element_name)

                        element = self.find_by_name(element_name)

                    element_tag = element.tag_name

                    # If we catch div, this means we are working with radiobutton.
                    if element_tag == 'div':
                        if path != '':
                            element_name = '{}[{}]'.format(path, element_name.split('__')[1])
                        self.set_radio_element(element_name, val)

                    else:
                        element_type = element.get_attribute("type")

                        if element_tag == 'select':
                            self.set_select_element(element, val)
                        elif element_tag == 'input' and element_type == 'radio':
                            self.set_radio_element(element_name, val)
                        elif element_tag == 'input' and element_type == 'checkbox':
                            self.set_checkbox_element(element)
                        else:
                            self.set_input_element(element, val)
                except Exception as ex:
                    print("Error happens on element: ", key, val)
                    raise ex
            else:
                self.fill_form(val, key)

    def _set_up(self):
        # Creation of instance of the browser.
        desired = DesiredCapabilities.CHROME
        desired['loggingPrefs'] = {'browser': 'ALL'}
        desired['pageLoadStrategy'] = 'none'
        self.driver = webdriver.Chrome(desired_capabilities=desired)
        self.driver.implicitly_wait(10)

        # Go to URL.
        if config.DOMAIN.startswith("http"):
            self.driver.get(config.DOMAIN + self.URL)
        else:
            raise Exception("Invalid domain name. Use 'http' or 'https' before domain name.!")

        # Delay for Angel.co-site.
        time.sleep(config.DELAY2 / 2)

        # Disable animations.
        self.driver.execute_script(
            "var style=document.createElement('style');"
            "style.type='text/css';style.appendChild("
            "document.createTextNode('*{transition: none !important;"
            "transition-property: none !important; transform: none !important;"
            "animation: none !important;}'));"
            "document.getElementsByTagName('head')[0].appendChild(style);"
        )

        # Maximize window size.
        self.driver.set_window_size(1280, 800, self.driver.window_handles[0])

    def _tear_down(self):
        # Close the instance of the browser.
        self.driver.quit()

    def set_radio_element(self, element_name, val):
        """A method for setting radio button element on the page."""

        radio_elements = self.find_by_name_many(element_name)

        for element in radio_elements:
            if element.get_attribute('value') == val:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);"
                    "arguments[0].click();", element
                )
                return True
        return False

    def set_select_element(self, element, val):
        """A method for selecting an option in the select element on the page."""

        element = ui.Select(element)
        return element.select_by_visible_text(val)

    def set_checkbox_element(self, element):
        """A method for setting checkbox element on the page."""

        if element.is_selected() != True:
            self.click(element)

    def set_input_element(self, element, val):
        """A method for typing text into input element on the page."""

        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.clear()
        element.send_keys(val)

    def wait_visibility_by_id(self, id_name, timeout=config.DELAY1):
        return ui.WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.ID, id_name)))

    def wait_visibility_by_name(self, name, timeout=config.DELAY1):
        return ui.WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.NAME, name)))

    def wait_visibility_by_name_many(self, name, timeout=config.DELAY1):
        return ui.WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_all_elements_located((By.NAME, name)))

    def wait_visibility_by_css(self, css_path, timeout=config.DELAY1):
        return ui.WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, css_path)))

    def wait_visibility_by_css_many(self, css_path, timeout=config.DELAY1):
        return ui.WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, css_path)))

    def wait_invisibility_by_css(self, css_path, timeout=config.DELAY1):
        return ui.WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, css_path)))

    def wait_invisibility(self, element, timeout=config.DELAY1):
        return ui.WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(element))

    def find_clickable_by_id(self, id_name, timeout=config.DELAY1):
        return ui.WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.ID, id_name)))

    def find_clickable_by_name(self, name, timeout=config.DELAY1):
        return ui.WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.NAME, name)))

    def find_clickable_by_css(self, css_path, timeout=config.DELAY1):
        return ui.WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_path)))

    def find_by_id(self, id_name):
        return self.driver.find_element_by_id(id_name)

    def find_by_name(self, name):
        return self.driver.find_element_by_name(name)

    def find_by_name_many(self, name):
        return self.driver.find_elements_by_name(name)

    def find_by_css(self, css_path):
        return self.driver.find_element_by_css_selector(css_path)

    def find_by_css_many(self, css_path):
        return self.driver.find_elements_by_css_selector(css_path)

    def find_by_link(self, link_text):
        return self.driver.find_elements_by_link_text(link_text)

    def find_by_xpath(self, xpath):
        return self.driver.find_element_by_xpath(xpath)

    def find_by_xpath_many(self, xpath):
        return self.driver.find_elements_by_xpath(xpath)

    def click(self, element):
        """A method for a clicking on the element on the page."""

        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()

    def print_logs(self):
        """A method for a printing logs of the console of the browser in the terminal."""

        logs = self.driver.get_log('browser')
        for log in logs:
            print(str(log))

    def make_screenshot(self):
        """A method for making a screenshot of the screen."""

        self.driver.get_screenshot_as_file(config.ROOT_DIR +
                                           "/screenshots/" +
                                           str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) +
                                           ".png")

    def get_current_url(self):
        """A method for getting the current URL of page."""

        return self.driver.current_url

    def send_lead_data(self, data):
        """A method for sending data to the Django Admin."""

        # For live environment.
        res = requests.post(
            'https://api-email.growthfountain.com/lead',
            headers={
                'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2'
                                 'VyX2lkIjozMTQsImZpcnN0X25hbWUiOiJBYnJhaGFtIiwibGFz'
                                 'dF9uYW1lIjoiT3JkZW4iLCJ1c2VyX2lwIjoiMTcyLjE3LjAuMS'
                                 'IsInNpdGVfaWQiOjIzfQ.X2q-wrCy8xrtHCOeX04ZlxR7b92ny'
                                 'UnOZBWfHh_KenA'},
            data=json.dumps(data),
        )
        # For dev environment.
        """
        res = requests.post(
            'https://api-email-dev.growthfountain.com/lead',
            headers={
                'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2'
                                 'VyX2lkIjozMTQsImZpcnN0X25hbWUiOiJBYnJhaGFtIiwibGFz'
                                 'dF9uYW1lIjoiT3JkZW4iLCJ1c2VyX2lwIjoiMTcyLjE3LjAuMS'
                                 'IsInNpdGVfaWQiOjIzfQ.X2q-wrCy8xrtHCOeX04ZlxR7b92ny'
                                 'UnOZBWfHh_KenA'},
            data=json.dumps(data),
        )
        """
        print(res, res.text)
        time.sleep(config.DELAY2 / 10)

    def check_email(self, email):
        """A method for checking email for the "bad emails"."""

        for bad_email in bad_sites.BAD_EMAILS:
            # Search for good email with re.search function.
            if re.search(bad_email, email) is not None:
                return None
        return email

    def get_company_email(self, info):
        """A method for getting email from the company website."""

        res = requests.put(
            "https://api-email.growthfountain.com/lead/check", json={'website': info['website']},
            headers={
                'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2'
                                 'VyX2lkIjozMTQsImZpcnN0X25hbWUiOiJBYnJhaGFtIiwibGFz'
                                 'dF9uYW1lIjoiT3JkZW4iLCJ1c2VyX2lwIjoiMTcyLjE3LjAuMS'
                                 'IsInNpdGVfaWQiOjIzfQ.X2q-wrCy8xrtHCOeX04ZlxR7b92ny'
                                 'UnOZBWfHh_KenA'},
        )

        # For finding company email address we will just open company website.
        # And try to search for an email address in HTML source.
        if info['website'] and res != "1":
            email_regex = r'\b[\w.-]+?@\w+?\.\w+?\b'
            wait = WebDriverWait(self.driver, 1000)
            self.driver.get(info['website'])
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(config.DELAY2 * 2)
            self.driver.execute_script("window.stop();")
            emails = re.findall(email_regex, self.driver.page_source)

            for email, _ in groupby(emails):
                clean_email = self.check_email(email)

                # If we already found good email -- return it.
                if clean_email is not None:
                    return clean_email

        return None

    def scroll_down(self):
        """A method for scrolling the page."""

        # Get scroll height.
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to the bottom.
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page.
            time.sleep(config.SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height.
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
