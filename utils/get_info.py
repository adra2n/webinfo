import traceback

from bs4 import BeautifulSoup
import re
import requests
from libs.httplibs import requests_headers
import urllib3,ssl

# Ignore warning
urllib3.disable_warnings()
# Ignore ssl warning info.
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


headers={
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent':'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US)',
    'Upgrade-Insecure-Requests':'1','Connection':'keep-alive','Cache-Control':'max-age=0',
    'Accept-Encoding':'gzip, deflate, sdch','Accept-Language':'zh-CN,zh;q=0.8',
    "Referer": "http://www.baidu.com/link?url=www.so.com&url=www.soso.com&&url=www.sogou.com",
    'Cookie':"PHPSESSID=gljsd5c3ei5n813roo4878q203"}
# re
rtitle = re.compile(r'title="(.*)"')
rheader = re.compile(r'header="(.*)"')
rbody = re.compile(r'body="(.*)"')
rbracket = re.compile(r'\((.*)\)')

def get_info(url):
    try:
        req=requests.get(url, headers=headers,timeout=2, verify=False)
        content = req.text
        # print(req.apparent_encoding)
        # req.encoding = req.apparent_encoding
        if req.status_code == 200 or req.status_code == 500:
            try:
                soup = BeautifulSoup(content.lower(), "lxml")
                t = soup.title.text.strip('\n')
                # t = soup.title.text.strip('\n')
                return str(req.headers),content,t
            except:
                # traceback.print_exc()
                t = content[:10]
                return str(req.headers), content, t
    except:
        return '', 0, ''


def check_rule(key, header, body, title):
    """指纹识别"""
    try:
        if 'title="' in key:
            if re.findall(rtitle, key)[0].lower() in title.lower():
                return True
        elif 'body="' in key:
            if re.findall(rbody, key)[0] in body: return True
        else:
            if re.findall(rheader, key)[0] in header: return True
    except Exception as e:
        pass



# _,_,title=get_info("https://www.baidu.com")
# print(title)