from tqdm import tqdm
import joblib

import pandas as pd
import csv
import numpy.random as rand

from time import sleep
import re

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


import os
os.environ['MOZ_HEADLESS'] = '1'

from utils import get_links, load, platforms, remove_duplicates

##################################################################################


df_terms = pd.read_csv("terms.csv")
df_with_links = pd.read_csv("links.csv")
# chunk up to parallelise here?
# then save individual files below
# and merge later
    
##################################################################################

save_every = 5
num_links = 5
youtube_regex = re.compile(r'watch\?v=(.+?)"')
dailymotion_regex = re.compile(r'href="/video/(.+?)"')


##################################################################################


driver = webdriver.Firefox()

for i, row in tqdm(df_terms.iterrows(), total=df_terms.shape[0]):
    
    if row.done is True:
        continue
    
    url = platforms[row.platform](row.term)
    driver.get(url)
    sleep(2)
    page = driver.page_source
    
    rgx = youtube_regex if row.platform == "youtube" else dailymotion_regex
    
    matches = list(re.finditer(rgx, str(page)))
    links = list(remove_duplicates(m.group(1) for m in matches))
    
    for j, l in enumerate(links[:num_links]):
        df_with_links.at[(i*num_links)+j, "link"] = l
    
    df_terms.at[i, "done"] = True
    
    if i % save_every == 0:
        df_terms.to_csv("terms_filled.csv",  line_terminator="\n", quotechar='"', quoting=csv.QUOTE_ALL)
        df_with_links.to_csv("links_filled.csv",  line_terminator="\n", quotechar='"', quoting=csv.QUOTE_ALL)