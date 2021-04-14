#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import random
from datetime import date
import logging
import sys
import os
import atexit
import requests
import json

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidSessionIdException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from xvfbwrapper import Xvfb

# Start virtual display
VDISPLAY = Xvfb()
VDISPLAY.start()

# Run firefox in headless mode
OPTIONS = Options()
OPTIONS.add_argument("--headless")
# Do not wait for page to fully load
OPTIONS.page_load_strategy = 'none'

# Makes pages load faster
PROFILE = webdriver.FirefoxProfile()
PROFILE.set_preference("browser.privatebrowsing.autostart", True)
PROFILE.set_preference("network.http.pipelining", True)
PROFILE.set_preference("network.http.proxy.pipelining", True)
PROFILE.set_preference("network.http.pipelining.maxrequests", 8)
PROFILE.set_preference("content.notify.interval", 500000)
PROFILE.set_preference("content.notify.ontimer", True)
PROFILE.set_preference("content.switch.threshold", 250000)
PROFILE.set_preference("browser.cache.memory.capacity", 65536)
PROFILE.set_preference("browser.startup.homepage", "about:blank")
PROFILE.set_preference("reader.parse-on-load.enabled", False)
PROFILE.set_preference("browser.pocket.enabled", False)
PROFILE.set_preference("loop.enabled", False)
PROFILE.set_preference("browser.chrome.toolbar_style", 1)
PROFILE.set_preference("browser.display.show_image_placeholders", False)
PROFILE.set_preference("browser.display.use_document_colors", False)
PROFILE.set_preference("browser.display.use_document_fonts", 0)
PROFILE.set_preference("browser.formfill.enable", False)
PROFILE.set_preference("browser.helperApps.deleteTempFileOnExit", True)
PROFILE.set_preference("browser.shell.checkDefaultBrowser", False)
PROFILE.set_preference("browser.startup.homepage", "about:blank")
PROFILE.set_preference("browser.startup.page", 0)
PROFILE.set_preference("browser.tabs.forceHide", True)
PROFILE.set_preference("browser.urlbar.autoFill", False)
PROFILE.set_preference("browser.urlbar.autocomplete.enabled", False)
PROFILE.set_preference("browser.urlbar.showPopup", False)
PROFILE.set_preference("browser.urlbar.showSearch", False)
PROFILE.set_preference("extensions.checkCompatibility", False)
PROFILE.set_preference("extensions.checkUpdateSecurity", False)
PROFILE.set_preference("extensions.update.autoUpdateEnabled", False)
PROFILE.set_preference("extensions.update.enabled", False)
PROFILE.set_preference("general.startup.browser", False)
PROFILE.set_preference("plugin.default_plugin_disabled", False)
PROFILE.set_preference("permissions.default.image", 2)
PROFILE.set_preference("http.response.timeout", 5)
PROFILE.set_preference("dom.max_script_run_time", 5)
PROFILE.set_preference("webgl.disabled", True)

global DRIVER
DRIVER = webdriver.Firefox(firefox_profile=PROFILE, firefox_binary='/usr/bin/firefox', executable_path='./geckodriver', options=OPTIONS)
DRIVER.set_page_load_timeout(5)

# Logging setup
logging.basicConfig(filename='logs/' + str(date.today()), format='%(asctime)s %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

# Send notification to device(s)
def notify(title, message, url=None):
    token = 'a6j96sdv4z8j3jifiofo2for72fr6b'
    user = 'ucseovragtfce3ibsnocdxx64x3bx4'
    data = {'token':token, 'user':user, 'message':message, 'device':'iphone', 'title':title, 'priority':'1'}
    if url is not None:
        data['url'] = url
    r = requests.post("https://api.pushover.net/1/messages.json", data=data)

    if int(r.status_code) == 200:
        logging.info('Notification posted.')
    else:
        logging.error('Notification post failed with status: ' + r.status_code + ' ' + r.reason)

# Exit handler with cleanup
def exit_handler():
    exit_message = "Application exiting..."
    logging.info(exit_message)
    notify(exit_message, 'Bye!')
    DRIVER.quit()
    VDISPLAY.stop()
    sys.exit()

atexit.register(exit_handler)

# App configuration manager
class ConfigManager:
    CONFIG_FNAME = 'config.json'
    CONFIG_VAL_TEST_ENABLED = 'Test enabled'
    CONFIG_VAL_VERBOSE = 'Verbose'
    CONFIG_VAL_PAGE_LOAD_TIMEOUT = 'Page load timeout'
    CONFIG_VAL_NOTIFICATION_INTERVAL = 'Notification interval'
    CONFIG_VAL_NOTIFICATION_LIMIT = 'Notification limit'
    CONFIG_VAL_NOTIFICATION_TOKEN = 'Notification token'
    CONFIG_VAL_NOTIFICATION_USERID = 'Notification userid'
    CONFIG_VAL_NOTIFICATION_DEVICE = 'Notification device'
    def __init__(self):
        self.update_config()

    def update_config(self):
        self.config = json.load(open(self.CONFIG_FNAME))

    def get_notification_interval(self):
        return self.config[self.CONFIG_VAL_NOTIFICATION_INTERVAL]

    def get_notification_limit(self):
        return self.config[self.CONFIG_VAL_NOTIFICATION_LIMIT]

    def get_notification_device(self):
        return self.config[self.CONFIG_VAL_NOTIFICATION_DEVICE]

    def get_notification_token(self):
        return self.config[self.CONFIG_VAL_NOTIFICATION_TOKEN]

    def get_notification_userid(self):
        return self.config[self.CONFIG_VAL_NOTIFICATION_USERID]

    def get_page_load_timeout(self):
        return self.config[self.CONFIG_VAL_PAGE_LOAD_TIMEOUT]

    def test_enabled(self):
        return self.config[self.CONFIG_VAL_TEST_ENABLED]

    def page_enabled(self, page_ID):
        try:
            return self.config[page_ID]
        except KeyError:
            return False

# Status of recent notifications
class NotificationStatus:
    def __init__(self):
        self.last_notification_sent = 0.0
        self.recent_notifications = 0

    def notification_sent(self):
        self.last_notification_sent = time.time()
        self.recent_notifications += 1

    def is_limited(self, interval, limit):
        now = time.time()
        if (now - self.last_notification_sent) >= interval:
            self.recent_notifications = 0

        if self.recent_notifications >= limit:
            return True
        else:
            return False

# Used to track and limit the number of notifications sent for each page
class NotificationLimiter:
    def __init__(self, pages):
        self.notification_interval = 60
        self.notification_limit = 2
        self.page_notifications = {}
        for page in pages:
            self.page_notifications[page.ID] = NotificationStatus()

    def get_notification_status(self, ID):
        return self.page_notifications[ID]

    def update_limits(self, interval, limit):
        self.notification_interval = interval
        self.notification_limit = limit

# Simple page
class Page:
    def __init__(self, edition, name, url, stock_xpath, price_xpath, cart_xpath=None, test=False):
        # Console edition
        self.edition = edition
        # Page name
        self.name = name
        # Unique ID
        self.ID = " ".join([name, edition])
        # Page url
        self.url = url
        # Xpath to element that describes stock
        self.stock_xpath = stock_xpath
        # Xpath to element that describes price
        self.price_xpath = price_xpath
        # Xpath to "add to cart" button
        self.cart_xpath = cart_xpath
        # Whether page used for testing
        self.test = test

# Amazon page
class AmazonPage(Page):
    def __init__(self, edition, name, url, stock_xpath, price_xpath, sed_button_xpath=None, ded_button_xpath=None, cart_xpath=None, test=False):
        super().__init__(edition, name, url, stock_xpath, price_xpath, cart_xpath=cart_xpath, test=test)
        # Button to select standard ps5 edition
        self.sed_button_xpath = sed_button_xpath
        # Button to select digital ps5 edition
        self.ded_button_xpath = ded_button_xpath

# Page names
PAGE_AMAZONNL = 'Amazon.nl'
PAGE_AMAZONDE = 'Amazon.de'
PAGE_AMAZONIT = 'Amazon.it'
PAGE_AMAZONES = 'Amazon.es'
PAGE_AMAZONFR = 'Amazon.fr'
PAGE_AMAZONPL = 'Amazon.pl'
PAGE_AMAZONUK = 'Amazon.co.uk'
PAGE_TOPO = 'Topocentras.lt'
PAGE_TECHNO = 'Technorama.lt'
PAGE_GAMEROOM = 'Gameroom.lt'

pages = []

pages.append(Page(
"Digital",
PAGE_TOPO,
"https://www.topocentras.lt/zaidimu-kompiuteris-sony-playstation-5-digital.html",
"//*[@id='productPage']/div[2]/div[2]/div[1]/h1",
"//*[@id='productPage']/div[3]/div[2]/div[2]/div/div[1]/div/div/div[3]/span",))

pages.append(Page(
"Digital",
PAGE_TOPO,
"https://www.topocentras.lt/zaidimu-pultas-sony-dualsense-ps5.html",
"//*[@id='productPage']/div[2]/div[2]/div[1]/h1",
"//*[@id='productPage']/div[3]/div[2]/div[2]/div/div[1]/div/div/div[3]/span",
test=True))

pages.append(Page(
"Standard",
PAGE_TOPO,
"https://www.topocentras.lt/zaidimu-kompiuteris-sony-playstation-5.html",
"//*[@id='productPage']/div[2]/div[2]/div[1]/h1",
"//*[@id='productPage']/div[3]/div[2]/div[2]/div/div[1]/div/div/div[3]/span"))

# pages.append(Page(
# 'Digital',
# PAGE_TOPO,
# "https://www.topocentras.lt/catalogsearch/result/?q=playstation%205",
# "//*[@id='categoryPage']/div[3]/div[1]/div[7]/div[3]/div/span",
# "//*[@id='filterContainer']/div[1]/strong"))

# pages.append(Page(
# PAGE_GAMEROOM,
# # "https://gameroom.lt/lt/playstation-4-pro-konsoles/products/zaidimu-konsole-sony-playstation-4-ps4-pro-1tb-439",
# "https://gameroom.lt/lt/playstation-5-konsoles/products/playstation-5-zaidimu-konsole-825gb-ps5-4299",
# # "https://gameroom.lt/lt/playstation-5-konsoles/products/playstation-5-digital-edition-zaidimu-konsole-825gb-ps5-4300",
# "//*[@id='availability_value']",
# "//*[@id='our_price_display']",
# cart_xpath="//*[@id='add_to_cart']"))

# pages.append(Page(
# 'Digital',
# PAGE_GAMEROOM,
# "https://gameroom.lt/lt/playstation-5-konsoles/products/playstation-5-digital-edition-zaidimu-konsole-825gb-ps5-dualsense-valdiklis-pakrovimo-stovas-5725",
# "//*[@id='availability_value']",
# "//*[@id='our_price_display']",
# cart_xpath="//*[@id='add_to_cart']"))

# pages.append(Page(
# 'Digital',
# PAGE_GAMEROOM,
# "https://gameroom.lt/lt/sony-playstation/products/the-last-of-us-part-ii-654",
# "//*[@id='availability_value']",
# "//*[@id='our_price_display']",
# cart_xpath="//*[@id='add_to_cart']"))

pages.append(AmazonPage(
"Digital",
PAGE_AMAZONUK,
"https://www.amazon.co.uk/PlayStation-5-Digital-Edition-Console/dp/B08H97NYGP",
"//*[@id='availability']/span",
"//*[@id='priceblock_ourprice']"))

pages.append(AmazonPage(
"Digital",
PAGE_AMAZONDE,
"https://www.amazon.de/dp/B08H98GVK8",
"//*[@id='availability']/span",
"//*[@id='priceblock_ourprice']"))

pages.append(AmazonPage(
"Standard",
PAGE_AMAZONDE,
"https://www.amazon.de/dp/B08H93ZRK9",
"//*[@id='availability']/span",
"//*[@id='priceblock_ourprice']"))

pages.append(AmazonPage(
"Digital",
PAGE_AMAZONPL,
"https://www.amazon.pl/Sony-PlayStation-5-Digital-Edition/dp/B08H98GVK8",
"//*[@id='availability']/span",
"//*[@id='priceblock_ourprice']"))

pages.append(AmazonPage(
"Standard",
PAGE_AMAZONIT,
"https://www.amazon.it/Playstation-Sony-PlayStation-5/dp/B08KKJ37F7",
"//*[@id='availability']/span",
"//*[@id='priceblock_ourprice']"))

pages.append(AmazonPage(
"Digital",
PAGE_AMAZONIT,
"https://www.amazon.it/_itm/dp/B08KJF2D25",
"//*[@id='availability']/span",
"//*[@id='priceblock_ourprice']"))

pages.append(AmazonPage(
"Digital",
PAGE_AMAZONIT,
"https://www.amazon.it/Sony-PlayStation%C2%AE5-DualSenseTM-Wireless-Controller/dp/B08H99BPJN",
"//*[@id='availability']/span",
"//*[@id='priceblock_ourprice']",
test=True))

pages.append(AmazonPage(
"Standard",
PAGE_AMAZONES,
"https://www.amazon.es/dp/B08KKJ37F7",
"//*[@id='availability']/span",
"//*[@id='priceblock_ourprice']"))

pages.append(AmazonPage(
"Digital",
PAGE_AMAZONES,
"https://www.amazon.es/dp/B08KJF2D25",
"//*[@id='availability']/span",
"//*[@id='priceblock_ourprice']"))

pages.append(AmazonPage(
"Standard",
PAGE_AMAZONFR,
"https://www.amazon.fr/PlayStation-%C3%89dition-Standard-DualSense-Couleur/dp/B08H93ZRK9",
"//*[@id='availability']/span",
"//*[@id='priceblock_ourprice']"))

pages.append(AmazonPage(
"Digital",
PAGE_AMAZONFR,
"https://www.amazon.fr/PlayStation-Digital-Manette-DualSense-Couleur/dp/B08H98GVK8",
"//*[@id='availability']/span",
"//*[@id='priceblock_ourprice']"))

# pages.append(AmazonPage(
# PAGE_AMAZONNL,
# "https://www.amazon.nl/-/en/dp/B08H93ZRK9",
# "//*[@id='availability']/span",
# "//*[@id='priceblock_ourprice']",
# "//*[@id='a-autoid-13-announce']",
# "//*[@id='a-autoid-14-announce']"))

NOTIFICATION_LIMITER = NotificationLimiter(pages)
CONFIG_MANAGER = ConfigManager()

def randinrange(range):
    return range[0] + (range[1]-range[0])*random.random()

def ps5_detected(page, reason, price):
    notification_status = None
    can_send_notification = False
    limit_reached = False
    try:
        notification_status = NOTIFICATION_LIMITER.get_notification_status(page.ID)
    except KeyError:
        logging.error("Notification limit could not be found for page: " + page.ID)

    if notification_status is not None:
        notification_interval = NOTIFICATION_LIMITER.notification_interval
        notification_limit = NOTIFICATION_LIMITER.notification_limit
        if not notification_status.is_limited(notification_interval, notification_limit):
            can_send_notification = True
            notification_status.notification_sent()
            if notification_status.is_limited(notification_interval, notification_limit):
                limit_reached = True

    title = page.ID
    message = " ".join([reason, price])

    if limit_reached:
        message = "Limit reached! " + message
    if not can_send_notification:
        message = "Limited! " + message
        logging.warning("Notification limit reached.")

    print_text = " | ".join([title, message])
    logging.info(print_text)

    if can_send_notification:
        notify(title, message, page.url)

def extract_text(element):
    text = ''.join(map(lambda x: x.text, element)).strip()
    return text

def stock_price_from_xpath(driver, page):
    # Wait until the stock element has loaded, then extract it
    try:
        el = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element_by_xpath(page.stock_xpath))
    except Exception:
        pass
    try:
        extracted_stock = extract_text(driver.find_elements_by_xpath(page.stock_xpath))
        extracted_price = extract_text(driver.find_elements_by_xpath(page.price_xpath))
    except StaleElementReferenceException:
        restart_program()

    return (extracted_stock, extracted_price)

def detect_amazon(page, stock, price):
    if stock == '':
        logging.warning("Amazon page empty stock element: " + page.ID)
        return
    if page.name == PAGE_AMAZONPL:
        if 'Obecnie niedostępny' not in stock:
            ps5_detected(page, stock, price)
    elif page.name == PAGE_AMAZONIT:
        if 'Non disponibile' not in stock:
            ps5_detected(page, stock, price)
    elif page.name == PAGE_AMAZONES:
        if 'No disponible' not in stock:
            ps5_detected(page, stock, price)
    elif page.name == PAGE_AMAZONFR:
        if 'indisponible' not in stock and 'de ces vendeurs' not in stock:
            ps5_detected(page, stock, price)
    elif page.name == PAGE_AMAZONDE:
        if 'nicht verfügbar' not in stock:
            ps5_detected(page, stock, price)
    elif 'unavailable' not in stock:
        ps5_detected(page, stock, price)

# def tryclickncheck(driver, button_xpath, stock_xpath, price_xpath, page_name):
#     def tryclick(driver, button_xpath):
#         try:
#             button = driver.find_element_by_xpath(button_xpath)
#             button.click()
#             return True
#         except NoSuchElementException:
#             exc, _, _ = sys.exc_info()
#             logging.warning("Button was not found: " + str(exc))
#             return False
#         except Exception:
#             exc, _, _ = sys.exc_info()
#             logging.warning("Button could not be clicked: " + str(exc))
#             return False
#
#     try:
#         if not tryclick(driver, button_xpath):
#             logging.warning("Button click failed, skipping...")
#             return False
#         time.sleep(randinrange(TIME_SLEEP_AFTER_CLICK_RANGE))
#         stock, price = stock_price_from_xpath(driver, stock_xpath, price_xpath)
#         detect_amazon(stock, price, page_name)
#         return True
#     except IndexError:
#         exc, _, _ = sys.exc_info()
#         logging.warning("Some element could not be found: " + str(exc))
#         return False

def check_addtocart(driver, cart_xpath):
    if cart_xpath is not None:
        try:
            cart = driver.find_element_by_xpath(cart_xpath)
            driver.execute_script("arguments[0].click();", cart)
            return True
        except NoSuchElementException:
            exc, _, _ = sys.exc_info()
            logging.warning("Cart button could not be found: " + str(exc))
            return False
        except Exception:
            exc, _, _ = sys.exc_info()
            logging.warning("Cart button could not be found: " + str(exc))
            return False
    else:
        return True

def restart_program():
    notify("Restarting program.", "Check me.")
    DRIVER.quit()
    VDISPLAY.stop()
    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

logging.info("Starting loop...")
while True:
    start = time.time()
    CONFIG_MANAGER.update_config()
    NOTIFICATION_LIMITER.update_limits(CONFIG_MANAGER.get_notification_interval(), CONFIG_MANAGER.get_notification_limit())
    for page in pages:
        if not CONFIG_MANAGER.page_enabled(page.ID):
            continue
        if page.test and (not CONFIG_MANAGER.test_enabled()):
            continue

        try:
            DRIVER.get(page.url)
        except TimeoutException:
            logging.warning("Selenium timeout for page: " + page.ID)
        except InvalidSessionIdException:
            logging.error("InvalidSessionIdException. Restarting program.")
            restart_program()
        except:
            exc, _, _ = sys.exc_info()
            logging.error("Skipping page: " + page.ID + ' due to ' + str(exc))
            continue


        # Amazon pages that need clicking to access PS5 page
        # if page.name in (PAGE_AMAZONDE):
            # if not tryclickncheck(driver, page.sed_button_xpath, page.stock_xpath, page.price_xpath, page.name):
            #     logging.warning("Retrying Amazon click and check...")
            #     tryclickncheck(driver, page.sed_button_xpath, page.stock_xpath, page.price_xpath, page.name)

            # tryclickncheck(driver, page.ded_button_xpath, page.stock_xpath, page.price_xpath, page.name)
            # if not tryclickncheck(driver, page.ded_button_xpath, page.stock_xpath, page.price_xpath, page.name):
            #     logging.warning("Retrying Amazon click and check...")
            #     tryclickncheck(driver, page.ded_button_xpath, page.stock_xpath, page.price_xpath, page.name)

        if isinstance(page, AmazonPage):
            stock, price = stock_price_from_xpath(DRIVER, page)
            detect_amazon(page, stock, price)

        elif page.name in (PAGE_TOPO, PAGE_TECHNO, PAGE_GAMEROOM):
            # Temporary solution when there are no PS5 pages in PAGE_TOPO
            # try:
            #     msg = driver.find_element_by_xpath(page.stock_xpath).text
            #     if 'parduota' not in msg:
            #         ps5_detected('empty result', page.name, price, page.edition, page.url)
            # except:
            #     ps5_detected('empty result', page.name, "", page.edition, page.url)
            # try:
            #     msg = driver.find_element_by_xpath(page.price_xpath).text
            #     if '17' not in msg:
            #         ps5_detected('empty result', page.name, "", page.edition, page.url)
            # except:
            #     ps5_detected('empty result', page.name, price, page.edition, page.url)
            stock, price = stock_price_from_xpath(DRIVER, page)
            if stock == '' and check_addtocart(DRIVER, page.cart_xpath):
                ps5_detected(page, 'empty result', price)

    DRIVER.delete_all_cookies()
    end = time.time()
    logging.info("Loop pass completed (" + str(round(end-start)) + "s)")
