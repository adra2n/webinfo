# -*- coding:utf-8 -*-

import requests
import sys


def check(ip, port):
    try:
        if str(port) == '443' or str(port) == '8443':
            url = "https://{ip}:{port}/v2/keys".format(ip=str(ip), port=str(port))
            r = requests.get(url, timeout=1, verify=False, allow_redirects=False)

        else:
            url = "http://{ip}:{port}/v2/keys".format(ip=str(ip), port=str(port))
            r = requests.get(url, timeout=1, allow_redirects=False)

        if r.status_code == 200 and '''"action":"get"''' in r.text:
            row = {
                "wakaka": 'ok',
                "level": "High",
                "vul": "ETCD 信息泄露，测试poc：{/v2/keys}"
            }
            print(row)
    except:
        pass


if __name__ == "__main__":
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        check(ip, port)
