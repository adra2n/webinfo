# coding:utf-8

# coding:utf-8

import requests
import sys
from pykafka import KafkaClient
import time


def check(ip, port):
    try:
        client = KafkaClient(hosts="{ip}:{port}".format(ip=ip, port=port), socket_timeout_ms=1000)
        topics = client.topics
        if topics:
            row = {
                "wakaka": 'ok',
                "level": "Medium",
                "vul": "Kafka 信息泄露"
            }
            print(row)

    except:
        pass


if __name__ == "__main__":
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        check(ip, port)
