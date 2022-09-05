# coding:utf-8

import requests
import sys


def check(ip, port):
    if str(port) == '443' or str(port) == '8443':
        docker_url_404 = "https://{ip}:{port}/".format(ip=str(ip), port=str(port))
        r = requests.get(docker_url_404, timeout=1, verify=False)
        if r.status_code == 404:
            docker_url_images = "https://{ip}:{port}/containers/json".format(ip=str(ip), port=str(port))
            r2 = requests.get(docker_url_images, timeout=1, verify=False, allow_redirects=False)
            if r2.text and "Image" in r2.text:
                row = {
                    "wakaka": 'ok',
                    "level": "High",
                    "vul": "docker 远程命令执行，测试POC:(/containers/json)"
                }
                print(row)

    else:
        docker_url_404 = "http://{ip}:{port}/".format(ip=str(ip), port=str(port))
        r = requests.get(docker_url_404, timeout=1)
        if r.status_code == 404:
            docker_url_images = "http://{ip}:{port}/containers/json".format(ip=str(ip), port=str(port))
            r2 = requests.get(docker_url_images, timeout=1, allow_redirects=False)
            if r2.text and "Image" in r2.text:
                row = {
                    "wakaka": 'ok',
                    "level": "High",
                    "vul": "docker 远程命令执行，测试POC:(/containers/json)"
                }
                print(row)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        check(ip, port)
