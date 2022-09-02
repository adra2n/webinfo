# coding:utf-8

import requests
import sys


def check(ip, port):
    try:
        if str(port) == '443' or str(port) == '8443':
            url = "https://" + str(ip) + ":" + str(port) + "/api/v1/nodes"
            r = requests.get(url, timeout=1, verify=False, allow_redirects=False)
        else:
            url = "http://" + str(ip) + ":" + str(port) + "/api/v1/nodes"
            r = requests.get(url, timeout=1, allow_redirects=False)

        res = r.text
        text = res.encode('utf-8')
        if r.status_code == 200 and b"items" in text:
            row = {
                "wakaka": "ok",
                "level": "High",
                "vul": "Kubernetes 未授权访问，测试poc:(/api/v1/nodes)"
            }
            print(row)
    except:
        pass


if __name__ == "__main__":
    if len(sys.argv) == 3:
        target = sys.argv[1]
        port = sys.argv[2]
        check(target, port)
# check("114.55.130.182", 8081)
