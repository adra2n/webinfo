# coding:utf-8

import socket
import sys
import traceback


class memcache():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def check(self):
        try:
            self.s.settimeout(5.0)
            self.s.connect((self.ip, self.port))
            self.s.send(b"stats\r\n")
            data = self.s.recv(1024)
            # print(123123)
            if b"STAT version" in data:
                row = {
                    "wakaka": 'ok',
                    "level": "Medium",
                    "vul": "Memcache 未授权访问"
                }
                print(row)

            self.s.close()
        except:
            traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        mg = memcache(ip, port)
        mg.check()

# mg=memcache('188.165.50.251',11211)
# mg.check()