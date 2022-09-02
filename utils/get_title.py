import traceback

from bs4 import BeautifulSoup
import json
import requests


def gettitle(url):

    req=requests.get(url, timeout=2, verify=False)
    req.encoding = req.apparent_encoding
    if req.status_code == 200 or req.status_code == 500:
        html = req.text
        try:
            soup = BeautifulSoup(html.lower(), "lxml")
            t = soup.title.text.encode('utf8', 'ignore').decode("utf8")
            # print(t)
        except:
            # traceback.print_exc()
            t = html[:100]
        # print(t)
        return t


# print(gettitle("https://demo-ep.netease.com/v2/keys/"))