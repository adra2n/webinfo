# __author__ = 'gaohe'
# -*- coding:utf-8 -*-

import socket
import struct
import sys
import json


class jdwp():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def jdwp_connect(self):
        try:
            self.s.settimeout(4.0)
            self.s.connect((self.ip, self.port))
            packet_handshark = struct.pack('14B', 0x4a, 0x44, 0x57, 0x50, 0x2d, 0x48, 0x61, 0x6e, 0x64, 0x73, 0x68,
                                           0x61, 0x6b, 0x65)
            self.s.send(packet_handshark)
            # print self.s.send(packet_handshark)
            # print self.s.recv(1024)
            return self.s.recv(1024)
        except:
            return False

    def check(self):
        if self.jdwp_connect() == "JDWP-Handshake":
            # print 1111
            packet_version = struct.pack('11B', 0x00, 0x00, 0x00, 0x0b, 0x00, 0x00, 0x00, 0x09, 0x00, 0x01, 0x01)
            packet_version2 = struct.pack('11B', 0x00, 0x00, 0x00, 0x0b, 0x00, 0x00, 0x00, 0x09, 0x00, 0x01, 0x07)
            for i in [packet_version,packet_version2]:
                self.s.send(i)
                data = self.s.recv(1024)
                # print data
                if b'JVM Debug' in data or b'VM version' in data:
                    data = {
                        "wakaka": 'ok',
                        "level": "High",
                        "vul": "JDWP 远程命令执行"
                    }
                    print(json.dumps(data))

            else:
                pass
            self.s.close()

# jdb=jdwp('10.99.168.204', 5006)
# print jdb.jdwp_version()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        mg = jdwp(ip, port)
        mg.check()
