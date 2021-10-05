import os
import time
import requests

from bs4 import BeautifulSoup as bs4

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

from urllib3 import *



from urllib.parse import quote as url_quote
import re
from time import sleep



platforms = {"youtube": lambda s: f"https://www.youtube.com/results?search_query={s}&sp=EgYIBBABGAE%3D",
            "dailymotion": lambda s: f"https://www.dailymotion.com/search/{s}/videos?duration=mins_1_5&dateRange=past_month"}

youtube_regex = re.compile(r'watch\?v=(.+?)"')
dailymotion_regex = re.compile(r'href="/video/(.+?)"')



def load(f, n=-1):
    with open(f, encoding="utf8") as handle:
        return [l.strip() for l in handle if l.strip()][:n]


def remove_duplicates(ls):
    s = set()
    for x in ls:
        if not x in s:
            s.add(x)
            yield x

            
def click_button_if_exists(page, driver, do_quick_check=True):
    if do_quick_check:
        if re.search("VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc IIdkle",
                     page) is None: 
            return False
    
    slct = "#yDmH0d > c-wiz > div > div > div > div.NIoIEf > div.G4njw > div.qqtRac > form > div.lssxud > div > button"
    
    try:
        submit_button = driver.find_element_by_css_selector(slct)
        submit_button.click()
        print("button clicked!")
        return True
    except NoSuchElementException:
        return False
    

# def safe_get(driver, url, tries=5):
#     try:
#         driver.get(url)
#     except TimeoutException:
#         print("!! "*20)
#         print("TIMEOUT HAPPENED! WAITING 10 SECONDS THEN RESTARTING DRIVER")
#         driver.quit()
#         sleep(10)
#         print("WAITING DONE!")
        
#         driver = webdriver.Firefox()
#         driver.get(url)
#         print("GET DONE!")
        
# #         print(f"TIMEOUT HAPPENED! WAITING 10 SECONDS, TRYING {tries} TIMES!")
# #         sleep(10)



def safe_get(driver, url):
    try:
        driver.get(url)
        return driver.page_source, driver
    except TimeoutException:
        print("!! "*20)
        print("TIMEOUT HAPPENED! WAITING 10 SECONDS THEN RESTARTING DRIVER")
        driver.quit()
        sleep(10)
        driver = webdriver.Firefox()
        return None, driver
        
#         driver.get(url)
#         return driver.page_source, driver
#     except ConnectionRefusedError:
#         print("!! "*20)
#         print("CONNECTIONREFUSED HAPPENED! WAITING 10 SECONDS THEN RETURNING NONE")
#         sleep(10)
#         return None
# #         driver.get(url)
# #         return driver.page_source

        

def request_and_scroll(url, num_scrolls=0, driver=None, is_youtube=False):
    page = None
    while page is None:
        page, driver = safe_get(driver, url)
   
    if is_youtube:
        clicked = click_button_if_exists(page, driver, do_quick_check=True)
        
    for i in range(num_scrolls):
        driver.execute_script("window.scrollTo(1,5000)") # 5000000
        sleep(1)

#     driver.close()
    
    return page, driver


######################################


def check_no_results(pg, platform):
    if platform == "youtube":
        return find_video_links(pg, r'watch\?v=(.+?)"') == []
    elif platform == "dailymotion":
        return re.search("Search for something else or remove search filters.", pg) is not None


def find_video_links(page, regex):
    try:
        return list(remove_duplicates(m.group(1) for m in re.finditer(regex, str(page))))
    except IndexError:
        print(regex, [m.start() for m in re.finditer(regex, str(page))])


#######################################
        
        
def get_links(driver=None, platform=None, query=None, term=None, n=10):
    
    url = query(url_quote(term))
    
    result_page, driver = request_and_scroll(query(term), 
                                     num_scrolls=n, 
                                     driver=driver, 
                                     is_youtube=(platform == "youtube"))
    
    
    if platform == "youtube":
        r = youtube_regex
    elif platform == "dailymotion":
        r = dailymotion_regex
    else:
        raise ValueError(f"given platform {platform} is not defined!")
    
    if check_no_results(result_page, platform):
        return [None]
    
    
    return find_video_links(result_page, r), driver