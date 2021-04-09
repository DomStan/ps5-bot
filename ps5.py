#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from selenium import webdriver
from playsound import playsound
import random
from datetime import date
import logging
import sys
import os
import atexit
from subprocess import check_output

import requests

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidSessionIdException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from xvfbwrapper import Xvfb

# web driver setup
# xvfb = Xvfb()
# xvfb.start()

options = Options()
options.add_argument("--headless")
options.page_load_strategy = 'none'

profile = webdriver.FirefoxProfile()
profile.set_preference("browser.privatebrowsing.autostart", True)
profile.set_preference("network.http.pipelining", True)
profile.set_preference("network.http.proxy.pipelining", True)
profile.set_preference("network.http.pipelining.maxrequests", 8)
profile.set_preference("content.notify.interval", 500000)
profile.set_preference("content.notify.ontimer", True)
profile.set_preference("content.switch.threshold", 250000)
profile.set_preference("browser.cache.memory.capacity", 65536) # Increase the cache capacity.
profile.set_preference("browser.startup.homepage", "about:blank")
profile.set_preference("reader.parse-on-load.enabled", False) # Disable reader, we won't need that.
profile.set_preference("browser.pocket.enabled", False) # Duck pocket too!
profile.set_preference("loop.enabled", False)
profile.set_preference("browser.chrome.toolbar_style", 1) # Text on Toolbar instead of icons
profile.set_preference("browser.display.show_image_placeholders", False) # Don't show thumbnails on not loaded images.
profile.set_preference("browser.display.use_document_colors", False) # Don't show document colors.
profile.set_preference("browser.display.use_document_fonts", 0) # Don't load document fonts.
profile.set_preference("browser.formfill.enable", False) # Autofill on forms disabled.
profile.set_preference("browser.helperApps.deleteTempFileOnExit", True) # Delete temprorary files.
profile.set_preference("browser.shell.checkDefaultBrowser", False)
profile.set_preference("browser.startup.homepage", "about:blank")
profile.set_preference("browser.startup.page", 0) # blank
profile.set_preference("browser.tabs.forceHide", True) # Disable tabs, We won't need that.
profile.set_preference("browser.urlbar.autoFill", False) # Disable autofill on URL bar.
profile.set_preference("browser.urlbar.autocomplete.enabled", False) # Disable autocomplete on URL bar.
profile.set_preference("browser.urlbar.showPopup", False) # Disable list of URLs when typing on URL bar.
profile.set_preference("browser.urlbar.showSearch", False) # Disable search bar.
profile.set_preference("extensions.checkCompatibility", False) # Addon update disabled
profile.set_preference("extensions.checkUpdateSecurity", False)
profile.set_preference("extensions.update.autoUpdateEnabled", False)
profile.set_preference("extensions.update.enabled", False)
profile.set_preference("general.startup.browser", False)
profile.set_preference("plugin.default_plugin_disabled", False)
profile.set_preference("permissions.default.image", 2) # Image load disabled again
profile.set_preference("http.response.timeout", 5)
profile.set_preference("dom.max_script_run_time", 5)
profile.set_preference("webgl.disabled", True)

global DRIVER
DRIVER = webdriver.Firefox(firefox_profile=profile, firefox_binary='/usr/bin/firefox', executable_path='./geckodriver', options=options)
DRIVER.set_page_load_timeout(3)
DRIVER.implicitly_wait(1)

# logging setup
logging.basicConfig(filename='logs/' + str(date.today()), format='%(asctime)s %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)
#

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

# exit handler setup
def exit_handler():
    exit_message = "Application exiting..."
    logging.info(exit_message)
    notify(exit_message, 'Bye!')
    DRIVER.quit()
    sys.exit()

atexit.register(exit_handler)
#



class Page:
    def __init__(self, edition, name, url, stock_xpath, price_xpath, cart_xpath=None):
        self.edition = edition
        self.name = name
        self.url = url
        self.stock_xpath = stock_xpath
        self.price_xpath = price_xpath
        self.cart_xpath = cart_xpath

class AmazonPage(Page):
    def __init__(self, edition, name, url, stock_xpath, price_xpath, sed_button_xpath, ded_button_xpath, cart_xpath=None):
        super().__init__(edition, name, url, stock_xpath, price_xpath, cart_xpath=cart_xpath)
        self.sed_button_xpath = sed_button_xpath
        self.ded_button_xpath = ded_button_xpath

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

TIME_SLEEP_BETWEEN_PAGES = 3
TIME_SLEEP_BETWEEN_PAGES_AMAZON = 0
TIME_SLEEP_BETWEEN_LOOPS = 0
TIME_SLEEP_AFTER_CLICK_RANGE = (0.5, 0.5)

pages = []

pages.append(Page(
"Digital",
PAGE_TOPO,
"https://www.topocentras.lt/zaidimu-kompiuteris-sony-playstation-5-digital.html",
"//*[@id='productPage']/div[2]/div[2]/div[1]/h1",
"//*[@id='productPage']/div[3]/div[2]/div[2]/div/div[1]/div/div/div[3]/span"))
# pages.append(Page(
# "Standard",
# PAGE_TOPO,
# "https://www.topocentras.lt/zaidimu-kompiuteris-sony-playstation-5.html",
# "//*[@id='productPage']/div[2]/div[2]/div[1]/h1",
# "//*[@id='productPage']/div[3]/div[2]/div[2]/div/div[1]/div/div/div[3]/span"))

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
# pages.append(Page(
# PAGE_TECHNO,
# "https://www.technorama.lt/playstation-5/24600-konsole-sony-playstation-5-standart-edition-white.html",
# "//*[@id='outOfStockContainer']",
# "//*[@id='add-to-cart-or-refresh']/div[1]/div/div[1]/span"))


# pages.append(AmazonPage(
# "Digital",
# PAGE_AMAZONUK,
# "https://www.amazon.co.uk/PlayStation-5-Digital-Edition-Console/dp/B08H97NYGP",
# "//*[@id='availability']/span",
# "//*[@id='priceblock_ourprice']",
# "//*[@id='a-autoid-16-announce']",
# "//*[@id='a-autoid-17-announce']"))
#
# pages.append(AmazonPage(
# "Digital",
# PAGE_AMAZONDE,
# "https://www.amazon.de/dp/B08H98GVK8",
# "//*[@id='availability']/span",
# "//*[@id='priceblock_ourprice']",
# "//*[@id='a-autoid-16-announce']",
# "//*[@id='a-autoid-17-announce']"))

# pages.append(AmazonPage(
# PAGE_AMAZONDE,
# "https://www.amazon.de/dp/B08H93ZRK9",
# "//*[@id='availability']/span",
# "//*[@id='priceblock_ourprice']",
# "//*[@id='a-autoid-16-announce']",
# "//*[@id='a-autoid-17-announce']"))

pages.append(AmazonPage(
"Digital",
PAGE_AMAZONPL,
"https://www.amazon.pl/Sony-PlayStation-5-Digital-Edition/dp/B08H98GVK8",
"//*[@id='availability']/span",
"//*[@id='priceblock_ourprice']",
"//*[@id='a-autoid-16-announce']",
"//*[@id='a-autoid-17-announce']"))
#
# pages.append(AmazonPage(
# "Standard",
# PAGE_AMAZONIT,
# "https://www.amazon.it/Playstation-Sony-PlayStation-5/dp/B08KKJ37F7",
# "//*[@id='availability']/span",
# "//*[@id='priceblock_ourprice']",
# "//*[@id='a-autoid-13-announce']",
# "//*[@id='a-autoid-14-announce']"))
#
pages.append(AmazonPage(
"Digital",
PAGE_AMAZONIT,
"https://www.amazon.it/_itm/dp/B08KJF2D25",
"//*[@id='availability']/span",
"//*[@id='priceblock_ourprice']",
"//*[@id='a-autoid-13-announce']",
"//*[@id='a-autoid-14-announce']"))
#
# pages.append(AmazonPage(
# "Standard",
# PAGE_AMAZONES,
# "https://www.amazon.es/dp/B08KKJ37F7",
# "//*[@id='availability']/span",
# "//*[@id='priceblock_ourprice']",
# "//*[@id='a-autoid-13-announce']",
# "//*[@id='a-autoid-14-announce']"))
#
pages.append(AmazonPage(
"Digital",
PAGE_AMAZONES,
"https://www.amazon.es/dp/B08KJF2D25",
"//*[@id='availability']/span",
"//*[@id='priceblock_ourprice']",
"//*[@id='a-autoid-13-announce']",
"//*[@id='a-autoid-14-announce']"))

# pages.append(AmazonPage(
# PAGE_AMAZONFR,
# "https://www.amazon.fr/PlayStation-%C3%89dition-Standard-DualSense-Couleur/dp/B08H93ZRK9",
# "//*[@id='availability']/span",
# "//*[@id='priceblock_ourprice']",
# "//*[@id='a-autoid-13-announce']",
# "//*[@id='a-autoid-14-announce']"))

# pages.append(AmazonPage(
# "Digital",
# PAGE_AMAZONFR,
# "https://www.amazon.fr/PlayStation-Digital-Manette-DualSense-Couleur/dp/B08H98GVK8",
# "//*[@id='availability']/span",
# "//*[@id='priceblock_ourprice']",
# "//*[@id='a-autoid-13-announce']",
# "//*[@id='a-autoid-14-announce']"))

# pages.append(AmazonPage(
# PAGE_AMAZONNL,
# "https://www.amazon.nl/-/en/dp/B08H93ZRK9",
# "//*[@id='availability']/span",
# "//*[@id='priceblock_ourprice']",
# "//*[@id='a-autoid-13-announce']",
# "//*[@id='a-autoid-14-announce']"))

def randinrange(range):
    return range[0] + (range[1]-range[0])*random.random()

def yra_ps5(reason, page, price, edition, url):
    title = " ".join([page, edition])
    message = " ".join([price, reason])

    print_text = "\n".join(['\n', title, message, '\n'])
    logging.info(print_text)
    print(print_text)

    notify(title, message, url)

def extract_text(element):
    empty = 'empty element'
    text = ''.join(map(lambda x: x.text, element)).strip()
    if text == '':
        return empty
    else:
        return text

def stock_price_from_xpath(driver, stock_xpath, price_xpath):
    # result_stock = [""]
    # try:
    #     result_stock = WebDriverWait(driver, timeout=5).until(lambda d: d.find_element_by_xpath(stock_xpath))
    #     result_stock = [result_stock]
    # except Exception:
    #     pass
    result_stock = driver.find_elements_by_xpath(stock_xpath)
    result_price = driver.find_elements_by_xpath(price_xpath)
    extracted_price = extract_text(result_price)
    return (result_stock, extracted_price)


def detect_amazon(stock, price, page_name, page_edition, page_url):
    text = stock[0].text.strip()
    print(text)
    logging.info(text)
    if text == "":
        return
    if page_name == PAGE_AMAZONPL:
        if 'Obecnie niedostępny' not in text:
            yra_ps5(text, page_name, price, page_edition, page_url)
    elif page_name == PAGE_AMAZONIT:
        if 'Non disponibile' not in text:
            yra_ps5(text, page_name, price, page_edition, page_url)
    elif page_name == PAGE_AMAZONES:
        if 'No disponible' not in text:
            yra_ps5(text, page_name, price, page_edition, page_url)
    elif page_name == PAGE_AMAZONFR:
        if 'indisponible' not in text and 'de ces vendeurs' not in text:
            yra_ps5(text, page_name, price, page_edition, page_url)
    elif page_name == PAGE_AMAZONDE:
        if 'nicht verfügbar' not in text:
            yra_ps5(text, page_name, price, page_edition, page_url)
    elif 'unavailable' not in text:
        yra_ps5(text, page_name, price, page_edition, page_url)

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

logging.info("Starting loop...")
print("Starting loop...")
while True:
    start = time.time()
    for page in pages:
        try:
            output = check_output(DRIVER.get(page.url), timeout=3)
        except InvalidSessionIdException:
            print("Restarting program...")
            logging.warning("Restarting program...")
            os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
        except Exception:
            exc, _, _ = sys.exc_info()
            msg = "Refreshing page: " + str(exc)
            print(msg)
            logging.warning(msg)
            DRIVER.refresh()

        # time.sleep(randinrange([0, 1]))
        # time.sleep(TIME_SLEEP_BETWEEN_PAGES)
        # if page.name in (PAGE_AMAZONDE):
        #     time.sleep(TIME_SLEEP_AMAZON)
            # if not tryclickncheck(driver, page.sed_button_xpath, page.stock_xpath, page.price_xpath, page.name):
            #     logging.warning("Retrying Amazon click and check...")
            #     tryclickncheck(driver, page.sed_button_xpath, page.stock_xpath, page.price_xpath, page.name)

            # tryclickncheck(driver, page.ded_button_xpath, page.stock_xpath, page.price_xpath, page.name)
            # if not tryclickncheck(driver, page.ded_button_xpath, page.stock_xpath, page.price_xpath, page.name):
            #     logging.warning("Retrying Amazon click and check...")
            #     tryclickncheck(driver, page.ded_button_xpath, page.stock_xpath, page.price_xpath, page.name)

        if isinstance(page, AmazonPage):
            stock, price = stock_price_from_xpath(DRIVER, page.stock_xpath, page.price_xpath)
            detect_amazon(stock, price, page.name, page.edition, page.url)

        elif page.name in (PAGE_TOPO, PAGE_TECHNO, PAGE_GAMEROOM):
            # try:
            #     msg = driver.find_element_by_xpath(page.stock_xpath).text
            #     if 'parduota' not in msg:
            #         yra_ps5('empty result', page.name, price, page.edition, page.url)
            # except:
            #     yra_ps5('empty result', page.name, "", page.edition, page.url)
            # try:
            #     msg = driver.find_element_by_xpath(page.price_xpath).text
            #     if '17' not in msg:
            #         yra_ps5('empty result', page.name, "", page.edition, page.url)
            # except:
            #     yra_ps5('empty result', page.name, price, page.edition, page.url)
            stock, price = stock_price_from_xpath(DRIVER, page.stock_xpath, page.price_xpath)
            msg = extract_text(stock)
            print(msg)
            logging.info(msg)
            if stock[0]=="" and check_addtocart(DRIVER, page.cart_xpath):
                yra_ps5('empty result', page.name, price, page.edition, page.url)

    end = time.time()
    msg = "Loop pass completed (" + str(round(end-start)) + "s)"
    print(msg)
    logging.info(msg)
    DRIVER.delete_all_cookies()
