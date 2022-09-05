# coding:utf-8

import requests
import sys
import traceback


def check(ip, port):
    try:
        if str(port) == '443' or str(port) == '8443':
            url = "https://" + str(ip) + ":" + str(port)
            r = requests.get(url, timeout=1, verify=False, allow_redirects=False)
        else:
            url = "http://" + str(ip) + ":" + str(port)
            r = requests.get(url, timeout=1, allow_redirects=False)
        # print url
        # print(r.text)
        if r.status_code == 200 and "healthz" in r.text and "metrics" in r.text:
            row = {
                "wakaka": "ok",
                "level": "High",
                "vul": "Kubernetes 远程命令执行"
            }
            print(row)
    except:
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) == 3:
        target = sys.argv[1]
        port = sys.argv[2]
        check(target, port)
