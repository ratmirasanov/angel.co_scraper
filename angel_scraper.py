"""Module Angel for testing different features of Angel.co."""

import time
import traceback
import sys
import requests

from selenium.common import exceptions
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from utilities import Utilities
import config


class Angel(Utilities):
    """Class Angel for testing different features of Angel.co."""
    index = 0
    stop_file = None
    elements_on_page = 20
    begin_time = 0

    def login(self, email="", password=""):
        """A method for logging in to the Angel.co."""

        # Go to URL.
        self.driver.get(config.DOMAIN + "/login")

        # Finding elements on the page and actions.
        email_text_field_element = self.find_by_id("user_email")
        email_text_field_element.clear()
        email_text_field_element.send_keys(email)

        password_text_field_element = self.find_by_id("user_password")
        password_text_field_element.clear()
        password_text_field_element.send_keys(password)

        login_button_element = self.find_by_name("commit")
        self.click(login_button_element)
        time.sleep(config.DELAY2)

    def search_for_by_category(self, company_type="", city="", technology=""):
        """A method for searching companies by categories on the Angel.co."""

        # Go to URL.
        self.driver.get(config.DOMAIN + "/companies")

        self.wait_visibility_by_css_many(".base.startup")

        # Finding elements on the page and actions.
        search_div_field_element = self.find_by_css(".search-box")
        search_div_field_element.click()

        self.wait_visibility_by_css(".search-box .data_entry>input")

        search_text_field_element = self.find_by_css(".search-box .data_entry>input")
        search_text_field_element.clear()
        search_text_field_element.send_keys(company_type)
        search_text_field_element.send_keys(Keys.ENTER)

        search_text_field_element.send_keys(city)
        search_text_field_element.send_keys(Keys.ENTER)

        search_text_field_element.send_keys(technology)
        search_text_field_element.send_keys(Keys.ENTER)

    def open_company(self, link):
        """A method for opening page via link on the Angel.co."""

        arg = "window.open(\'" + link + "\', 'new_window')"
        self.driver.execute_script(arg)

        self.driver.switch_to.window(self.driver.window_handles[1])

        time.sleep(config.DELAY2 * 1.5)

        try:
            categories = self.find_by_css(".js-market_tag_holder").text
        except (exceptions.TimeoutException, exceptions.NoSuchElementException):
            categories = "-"

        try:
            company_info = {
                'company': self.find_by_css(".u-fontWeight500.s-vgBottom0_5").text,
                'note': "Categories: " + categories.replace("·", "-") +
                        "\n" + "Location: " + self.find_by_css(".js-location_tags").text,
                'website': self.find_by_css(".u-uncoloredLink.company_url").get_attribute("href")
            }
        except (exceptions.TimeoutException, exceptions.NoSuchElementException):
            return False

        company_info['email'] = self.get_company_email(company_info)

        if company_info['email'] is not None:
            company_info['source'] = "Angel.co"
            self.send_lead_data(company_info)

        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def scrape_page(self):
        """A method will open Angel page is url != None."""

        time.sleep(config.DELAY2)
        self.scroll_down()

        urls = []
        a_text_list = []

        company_div_list = self.find_by_css_many(".base.startup")[
            self.index:self.index + self.elements_on_page
        ]

        for company_div in company_div_list:
            text = company_div.find_element_by_css_selector(
                ".column.company_size .value").get_attribute("innerText")

            # If li element have 1-10 employees word.
            if text == "" or text == "1-10" or text == "11-50":
                company_name = company_div.find_elements_by_css_selector(
                    ".startup-link")[1]
                res = requests.put(
                    "https://api-email.growthfountain.com/lead/check",
                    json={'company': company_name.text},
                    headers={
                        'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2'
                                         'VyX2lkIjozMTQsImZpcnN0X25hbWUiOiJBYnJhaGFtIiwibGFz'
                                         'dF9uYW1lIjoiT3JkZW4iLCJ1c2VyX2lwIjoiMTcyLjE3LjAuMS'
                                         'IsInNpdGVfaWQiOjIzfQ.X2q-wrCy8xrtHCOeX04ZlxR7b92ny'
                                         'UnOZBWfHh_KenA'},
                )
                if res.text != "1":
                    urls.append(company_div.find_elements_by_css_selector(
                        ".startup-link"
                    )[0].get_attribute("href"))
                    a_text_list.append(company_div.find_elements_by_css_selector(
                        ".startup-link"
                    )[1].text)

        self.current_url = self.get_current_url()

        for url_local, a_text in zip(urls, a_text_list):
            current_time = time.time()
            if current_time - self.begin_time < config.TIMER:
                time.sleep(config.DELAY2)
                hover_company = self.find_by_xpath("//a[text()=\"" + a_text + "\"]")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", hover_company)
                hover = ActionChains(self.driver).move_to_element(
                    self.find_by_xpath("//a[text()=\"" + a_text + "\"]"))
                hover.perform()
                time.sleep(config.DELAY_COMPANY)
                self.open_company(url_local)
                time.sleep(config.DELAY_COMPANY)
            else:
                self._tear_down()
                self.stop_file.seek(0)
                self.stop_file.truncate()
                self.stop_file.write("{}".format(self.index))
                self.stop_file.close()
                sys.exit()

        more_link = None
        try:
            more_link = self.find_by_css(".more")
            self.index += self.elements_on_page
            self.stop_file.seek(0)
            self.stop_file.truncate()
            self.stop_file.write("{}".format(self.index))
            self.stop_file.flush()
            time.sleep(config.DELAY_COMPANY)
            self.click(more_link)
            self.scrape_page()
        except exceptions.TimeoutException:
            self.current_url = ""

    def start(self):
        """A method for getting information about companies on the Angel.co."""

        self.current_url = ""
        self.begin_time = time.time()

        try:
            self.stop_file = open("csv/angel.ti", "r")
            data = self.stop_file.read().split("\n")
            self.index = int(data[0])
            self.stop_file.close()
        except:
            print("Cannot read history file: ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** print_exception:")
            # exc_type below is ignored on 3.5 and later.
            traceback.print_exception(exc_type, exc_value,
                                      exc_traceback, limit=2, file=sys.stdout)

        self.stop_file = open("csv/angel.ti", "w+")

        self._set_up()

        self.login(config.EMAIL, config.PASSWORD)

        self.search_for_by_category("Mobile App", "New York City", "Python")
        time.sleep(config.DELAY2)

        if self.index != 0:
            for i in range(int(self.index / self.elements_on_page)):
                more_link = self.find_by_css(".more")
                self.click(more_link)
                self.scroll_down()

        self.scrape_page()

        self._tear_down()
        self.stop_file.close()


if __name__ == '__main__':
    ANGEL = Angel()
    ANGEL.start()
