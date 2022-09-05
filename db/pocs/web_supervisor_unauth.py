# coding:utf-8

import requests
import sys


def check(ip, port):
    try:
        if str(port) == '443' or str(port) == '8443':
            url = "https://" + ip + ":" + str(port) + "/"
            req = requests.get(url, timeout=1, verify=False, allow_redirects=False)
        else:
            url = "http://" + ip + ":" + str(port) + "/"
            req = requests.get(url, timeout=1, allow_redirects=False)

        if req.status_code == 200 and 'Supervisor' in req.text:
            row = {
                "wakaka": "ok",
                "level": "High",
                "vul": "Supervisor 未授权访问"
            }
            print(row)
    except:
        pass


if __name__ == "__main__":
    if len(sys.argv) == 3:
        target = sys.argv[1]
        port = sys.argv[2]
        check(target, port)
