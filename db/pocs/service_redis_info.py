# coding:utf-8

import socket
import sys
import traceback


class redis():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def check(self):
        try:
            self.s.settimeout(1.0)
            self.s.connect((self.ip, self.port))
            self.s.send(b"INFO\r\n")
            data = self.s.recv(1024)
            # print(data)
            if b"redis_version" in data:
                row = {
                    "wakaka": 'ok',
                    "level": "Medium",
                    "vul": "Redis 信息泄露"
                }
                print(row)

            self.s.close()
        except:
            # traceback.print_exc()
            pass
if __name__ == "__main__":
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        mg = redis(ip, port)
        mg.check()

# mg = redis("154.201.190.217",6379)
# mg.check()