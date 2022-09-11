# coding:utf-8
# coding:utf-8

import socket
import sys
import binascii
import traceback


class mongodb():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def check(self):
        try:
            socket.setdefaulttimeout(5.0)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip, int(self.port)))
            data = binascii.a2b_hex(
                "3a000000a741000000000000d40700000000000061646d696e2e24636d640000000000ffffffff130000001069736d6173746572000100000000")
            s.send(data)
            result = s.recv(1024)
            if b"ismaster" in result:
                getlog_data = binascii.a2b_hex(
                    "480000000200000000000000d40700000000000061646d696e2e24636d6400000000000100000021000000026765744c6f670010000000737461727475705761726e696e67730000")
                s.send(getlog_data)
                result = s.recv(1024)
                if b"totalLinesWritten" in result:
                    row = {
                        "wakaka": 'ok',
                        "level": "Medium",
                        "vul": "Mongodb 未授权访问"
                    }
                    print(row)
        except :
            # traceback.print_exc()
            pass
if __name__ == "__main__":
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        mg = mongodb(ip, port)
        mg.check()

# mg=mongodb("47.98.219.40",27017)
# mg.check()
