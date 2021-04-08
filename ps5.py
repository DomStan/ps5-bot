#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from selenium import webdriver
from playsound import playsound
import random
from datetime import date
import logging
import sys
import atexit

import requests

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from xvfbwrapper import Xvfb

# web driver setup
# xvfb = Xvfb(width=1280, height=720)
# xvfb.start()

options = Options()
# option for headless mode
options.add_argument("--headless")
DRIVER = webdriver.Firefox(firefox_binary='/usr/bin/firefox', executable_path='./geckodriver', options=options)
#

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
    notify(exit_message, 'Help!')
    # playsound('ding.mp3')
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
TIME_SLEEP_BETWEEN_PAGES_AMAZON = 1
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

# pages.append(AmazonPage(
# "Digital",
# PAGE_AMAZONPL,
# "https://www.amazon.pl/Sony-PlayStation-5-Digital-Edition/dp/B08H98GVK8",
# "//*[@id='availability']/span",
# "//*[@id='priceblock_ourprice']",
# "//*[@id='a-autoid-16-announce']",
# "//*[@id='a-autoid-17-announce']"))
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

    # playsound('notification.mp3')
    notify(title, message, url)

def extract_text(element):
    empty = 'empty element'
    text = ''.join(map(lambda x: x.text, element)).strip()
    if text == '':
        return empty
    else:
        return text

def stock_price_from_xpath(driver, stock_xpath, price_xpath):
    result_stock = driver.find_elements_by_xpath(stock_xpath)
    result_price = driver.find_elements_by_xpath(price_xpath)
    extracted_price = extract_text(result_price)
    return (result_stock, extracted_price)


def detect_amazon(stock, price, page_name, page_edition, page_url):
    text = stock[0].text.strip()
    print(text)
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
            DRIVER.get(page.url)
        except Exception:
            exc, _, _ = sys.exc_info()
            msg = "Loop skipped: " + str(exc)
            print(msg)
            logging.warning(msg)
            continue

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
            time.sleep(TIME_SLEEP_BETWEEN_PAGES_AMAZON)
            stock, price = stock_price_from_xpath(DRIVER, page.stock_xpath, page.price_xpath)
            detect_amazon(stock, price, page.name, page.edition, page.url)

        elif page.name in (PAGE_TOPO, PAGE_TECHNO, PAGE_GAMEROOM):
            time.sleep(TIME_SLEEP_BETWEEN_PAGES)
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
            print(extract_text(stock))
            if len(stock) == 0 and check_addtocart(DRIVER, page.cart_xpath):
                yra_ps5('empty result', page.name, price, page.edition, page.url)

    end = time.time()
    msg = "Loop pass completed (" + str(round(end-start)) + "s)"
    print(msg)
    logging.info(msg)
    time.sleep(TIME_SLEEP_BETWEEN_LOOPS)
