# coding:utf-8

import requests
import sys


def check(ip, port):
    path = "/noexistpath"
    try:
        if str(port) == '443' or str(port) == '8443':
            url = "https://" + str(ip) + ":" + str(port) + path
            r = requests.get(url, timeout=1, verify=False, allow_redirects=False)
        else:
            url = "http://" + str(ip) + ":" + str(port) + path
            r = requests.get(url, timeout=1, allow_redirects=False)

        if 'Using the URLconf defined in' in r.text and "Django settings" in r.text:
            row = {
                "wakaka": "ok",
                "level": "High",
                "vul": "Django 调试功能开启"
            }
            print(row)

        elif "DisallowedHost at" in r.text and 'ALLOWED_HOSTS' in r.text:
            row = {
                "wakaka": "ok",
                "level": "High",
                "vul": "Django 调试功能开启"
            }
            print(row)
    except:
        pass


if __name__ == "__main__":
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        check(ip, port)

# check("54.223.170.193", 8090)
