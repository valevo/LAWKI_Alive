from __future__ import unicode_literals
import youtube_dl

from time import time
from tqdm import tqdm

import pandas as pd

from youtube_dl import DownloadError

import pickle

from joblib import Parallel, delayed



def yt_expand(_id): return f"https://www.youtube.com/watch?v={_id}"
def dm_expand(_id): return f"https://www.dailymotion.com/video/{_id}"



# links = pd.read_csv("all_meta.csv")
links = pd.read_csv("links_test.csv")

            
            
def get_row(row):
    with youtube_dl.YoutubeDL(dict(quiet=True, verbose=False)) as ydl:
        expand = yt_expand if row.platform == "youtube" else dm_expand
        u = expand(row.link)


        try:
            dictMeta = ydl.extract_info(
                                u,
                            download=False)

            select_meta = dict(
                    id=dictMeta["id"],

                    channel=dictMeta["channel"] if "channel" in dictMeta else None,
                    title=dictMeta["title"],
                    description=dictMeta["description"],

                    date=dictMeta["upload_date"], # if "upload_date" in dictMeta else dictMeta["timestamp"],
                    views=dictMeta["view_count"],
                    duration=dictMeta["duration"],

                    tags=dictMeta["tags"],
                    categories=dictMeta["categories"] if "categories" in dictMeta else None,

                    age_limit=dictMeta["age_limit"],
    #                 average_rating=dictMeta["average_rating"],
                    like_count=dictMeta["like_count"] if "like_count" in dictMeta else None,
    #                 dislike_count=dictMeta["dislike_count"],
                )

            return select_meta

        except DownloadError as e:

            print(e, "\n", u)
            return dict(id=row.link)
            
            
            
            
            
            
dicts = Parallel(n_jobs=8, backend="loky")(delayed(get_row)(r) for i, r in tqdm(links.iterrows(), total=links.shape[0]))





            
with open("dicts.pkl", "wb") as handle:
    pickle.dump(dicts, handle)
