# coding:utf-8

import requests
import sys


def check(ip, port):
    try:
        if str(port) == '443' or str(port) == '8443':
            url = "https://" + str(ip) + ":" + str(port) + "/wd/hub/static/resource/hub.html"
            r = requests.get(url, timeout=1, verify=False,allow_redirects=False)
        else:
            url = "http://" + str(ip) + ":" + str(port) + "/wd/hub/static/resource/hub.html"
            r = requests.get(url, timeout=1, allow_redirects=False)

        if r.status_code == 200 and 'WebDriver Hub' in r.text:
            row = {
                "wakaka": "ok",
                "level": "High",
                "vul": "Selenium Grid Node 未授权访问，测试poc:(/wd/hub/static/resource/hub.html)"
            }
            print(row)
    except:
        pass


if __name__ == "__main__":
    if len(sys.argv) == 3:
        target = sys.argv[1]
        port = sys.argv[2]
        check(target, port)
