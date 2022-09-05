# coding:utf-8

# coding:utf-8

import requests
import sys
import json


def check(ip, port):
    path = "/ui/"
    try:
        if str(port) == '443' or str(port) == '8443':
            url = "https://" + str(ip) + ":" + str(port) + path
            r = requests.get(url, timeout=1, verify=False, allow_redirects=False)
        else:
            url = "http://" + str(ip) + ":" + str(port) + path
            r = requests.get(url, timeout=1, allow_redirects=False)

        if 'Consul by HashiCorp' in len(r.text) > 0:
            row = {
                "wakaka": "ok",
                "level": "High",
                "vul": "Consul 命令执行"
            }
            print(row)
    except:
        pass


if __name__ == "__main__":
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        check(ip, port)

# check("202.108.17.126:80", 80)
