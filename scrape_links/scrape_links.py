from tqdm import tqdm
import joblib

import pandas as pd
import numpy.random as rand

from time import sleep
import re

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


import os
os.environ['MOZ_HEADLESS'] = '1'

from utils import get_links, load, platforms

###

top_langs = ["en", "zh-cn", "hi", "es", "ar", "bn", "fr", "ru", "pt", "ur", "de", "jp", "id"]
n = -1
lang_d = {l: load(f"terms/{l}.txt", n) for l in top_langs}
    
trans_d = {}
for i, t in enumerate(lang_d["en"]):
    trans_d[t] = {l: lang_d[l][i] for l in lang_d}
    

    
###


records = []

driver = webdriver.Firefox()

num_links = 5

for p, f in platforms.items():
    progressbar = tqdm(trans_d.items(), desc=f"platform={p}")
    for topic, term_d in progressbar:
        for lang, term in term_d.items():
            progressbar.set_description(f"topic={topic}, lang={lang}")
            links, driver = get_links(platform=p, query=f, n=1, term=term, driver=driver)
            for l in links[:num_links]:
                records.append(
                    dict(
                         platform=p,
                         language=lang,
                         topic=topic,
                         term=term,
                         link=l
                    )
                )
        print(records)
                
    joblib.dump(records, f"records_{p}.pkl")
    
###


df = pd.DataFrame.from_records(records)
df.to_csv("links.csv", line_terminator="\n", quotechar='"', quoting=csv.QUOTE_ALL)