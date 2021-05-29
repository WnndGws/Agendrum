#!/usr/bin/env python
"""Downloads that days bing background image
"""

import json
import requests

def download_bing_wallpaper(country, resolution):
    """Downloads the daily wallpaper from bing as a png"""
    # idx determines where to start from. 0 is today, 1 is yesterday, etc.
    idx = "0"
    mkt = country
    url = f"https://www.bing.com/HPImageArchive.aspx?format=js&idx={idx}&n=1&mkt={mkt}"

    r = requests.get(url)
    if r.status_code == 200:
        json_dict = json.loads(r.content)["images"][0]
        image_url = json_dict["urlbase"]
        image_url = f"https://www.bing.com/{image_url}_{resolution}.jpg"
        r = requests.get(image_url)
        if r.status_code == 200:
            with open(f'/tmp/bing_{resolution}.jpg', "wb") as f:
                f.write(r.content)

if __name__ == "__main__":
    download_bing_wallpaper("en-AU", "1920x1080")
