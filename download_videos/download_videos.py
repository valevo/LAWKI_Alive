import youtube_dl

import numpy as np
import pandas as pd

from tqdm import tqdm
from time import time


def live_hook(d):
#     print("\n\n\n", d.keys(), d["duration"], "\n\n\n")
    
    if d["duration"] > 600:
        return f"duration > 600 (is {d['duration']})"
        
    if d["is_live"]:
        return "is_live"
    return None


def download(url_ls, prog):
    def u_pbar(d):
        if d["status"] == "downloading":
            prog.set_description(f"{d['filename']}: {d['_percent_str']} ({d['_speed_str']})")
        elif d["status"] == "finished":
            prog.update(1)
        else:
            return ValueError()

    ydl_opts = {
            'progress_hooks': [u_pbar],
            'quiet': True,
            'verbose': False,
            "writesubtitles": True,
            "subtitleslangs": "en",
            "subtitlesformat": "srt",
            "writethumbnail": False, #True,

            "download_archive": "downloaded.txt",

            "ignoreerrors": True,
            "outtmpl": "videos/%(id)s.%(ext)s",
        
            "format": "best",
            "socket_timeout": 1,
            "match_filter": live_hook
        }
        
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url_ls)



def yt_expand(_id): return f"https://www.youtube.com/watch?v={_id}"
def dm_expand(_id): return f"https://www.dailymotion.com/video/{_id}"


# feature_dir = "../features"

# links = pd.read_csv(f"{feature_dir}/features.csv")
# links = links.sort_values(by="link")


# new_durs = pd.read_csv("redownloaded_durations.csv")
# new_durs = new_durs.sort_values(by="id")

# links['duration'] = new_durs['duration']


# # filter and schedule

# links = links.dropna()
# links = links[links.duration <= 1000]
# scheduled = links.sample(frac=1.0, weights=1/(links.duration**2))


videos = pd.read_csv("links_filled.csv")

videos = videos[videos.link != "_"]

print(f"total of {videos.shape[0]} videos to be downloaded")

urls = [yt_expand(row.link) if row.platform == "youtube" else dm_expand(row.link)
           for i, row in videos.iterrows()]



import sys

if __name__ == "__main__":
    _, k, i = sys.argv
    
    k, i = int(k), int(i)
    assert i < k
    print(f"Downloading chunk {i} out of {k}...")
    
    chunks = np.array_split(urls, k)
    cur_urls = list(chunks[i])
    pbar = tqdm(total=len(cur_urls))
    
#     asd = '\n\t'.join(list(chunks[i]))
#     print(f"about to download:{asd}")
    

    download(cur_urls, pbar)
    