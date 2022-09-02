# coding:utf-8

import requests
import sys


def check(ip, port):
    for path in ['/v1/search', '/v2/keys']:
        try:
            if str(port) == '443' or str(port) == '8443':
                url = "https://{ip}:{port}/{path}".format(ip=str(ip), port=str(port), path=path)
                r = requests.get(url, timeout=1, verify=False, allow_redirects=False)

            else:
                url = "http://{ip}:{port}/{path}".format(ip=str(ip), port=str(port), path=path)
                r = requests.get(url, timeout=1, allow_redirects=False)

            if r.status_code == 200 and 'repositories' in r.text:
                row = {
                    "wakaka": "ok",
                    "level": "High",
                    "vul": "docker registry v2 信息泄露:(/v2/_catalog)"
                }
                print(row)

            elif r.status_code == 200 and 'num_results' in r.text:
                row = {
                    "wakaka": "ok",
                    "level": "High",
                    "vul": "docker registry v1 信息泄露:(/v1/search)"
                }
                print(row)
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) == 3:
        target = sys.argv[1]
        port = sys.argv[2]
        check(target, port)
