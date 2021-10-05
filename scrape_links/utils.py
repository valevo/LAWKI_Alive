import os
import time
import requests

from bs4 import BeautifulSoup as bs4

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException


from urllib.parse import quote as url_quote
import re
from time import sleep



platforms = {"youtube": lambda s: f"https://www.youtube.com/results?search_query={s}&sp=EgYIBBABGAE%3D",
            "dailymotion": lambda s: f"https://www.dailymotion.com/search/{s}/videos?duration=mins_1_5&dateRange=past_month"}

youtube_regex = r'watch\?v=(.+?)"'
dailymotion_regex = r'href="/video/(.+?)"'



def load(f, n=-1):
    with open(f, encoding="utf8") as handle:
        return [l.strip() for l in handle if l.strip()][:n]


def remove_duplicates(ls):
    s = set()
    for x in ls:
        if not x in s:
            s.add(x)
            yield x

            
def click_button_if_exists(driver, do_quick_check=True):
    if do_quick_check:
        pg = driver.page_source
        if re.search("VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc IIdkle",
         pg) is None: return False
    
    slct = "#yDmH0d > c-wiz > div > div > div > div.NIoIEf > div.G4njw > div.qqtRac > form > div.lssxud > div > button"
    try:
        submit_button = driver.find_element_by_css_selector(slct)
        submit_button.click()
        print("button clicked!")
        return True
    except NoSuchElementException:
        return False

    

def safe_get(driver, url, tries=5):
    try:
        driver.get(url)
    except TimeoutException:
        print("!! "*20)
        print("TIMEOUT HAPPENED! WAITING 10 SECONDS THEN RESTARTING DRIVER")
        driver.quit()
        sleep(10)
        print("WAITING DONE!)
        
        driver = webdriver.Firefox()
        driver.get(url)
        print("GET DONE!")
        
#         print(f"TIMEOUT HAPPENED! WAITING 10 SECONDS, TRYING {tries} TIMES!")
#         sleep(10)
        
        

def request_and_scroll(url, num_scrolls=1, driver=None, is_youtube=False):
    
    safe_get(driver, url)
    
    
    if is_youtube:
        clicked = click_button_if_exists(driver, do_quick_check=True)
        
    for i in range(num_scrolls):
        driver.execute_script("window.scrollTo(1,5000)") # 5000000
        sleep(1)

    page = str(driver.page_source)
        
#     driver.close()
    
    return page

######################################


def check_no_results(pg, platform):
    if platform == "youtube":
        return find_video_links(pg, r'watch\?v=(.+?)"') == []
    elif platform == "dailymotion":
        return re.search("Search for something else or remove search filters.", pg) is not None


def find_video_links(page, regex):
    find_video_urls = re.compile(regex)
    
    try:
        return list(remove_duplicates(m.group(1) for m in re.finditer(regex, str(page))))
    except IndexError:
        print(regex, [m.start() for m in re.finditer(regex, str(page))])

#######################################
        
        
def get_links(platform=None, query=None, term=None, n=10, driver=None):
    url = query(url_quote(term))
    result_page = request_and_scroll(query(term), num_scrolls=n, driver=driver, 
                                     is_youtube=(platform == "youtube"))
    
    
    if platform == "youtube":
        r = youtube_regex
    elif platform == "dailymotion":
        r = dailymotion_regex
    else:
        raise ValueError(f"given platform {platform} is not defined!")
    
    if check_no_results(result_page, platform):
        return [None]
    
    
    return find_video_links(result_page, r)