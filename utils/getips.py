# coding: utf-8

import struct
import time
import socket
import array
import threading
import os
import traceback

time_str = time.strftime('%X', time.localtime(time.time()))
mutex = threading.Lock()

class SendPingThr(threading.Thread):
    def __init__(self, ipPool, icmpPacket, icmpSocket, timeout=3):
        threading.Thread.__init__(self)
        self.Sock = icmpSocket
        self.ipPool = ipPool
        self.packet = icmpPacket
        self.timeout = timeout
        self.Sock.settimeout(timeout + 1)


    def run(self):
        for ip in self.ipPool:
            try:
                self.Sock.sendto(self.packet, (str(ip), 0))
            except socket.timeout:
                break
        time.sleep(self.timeout)


class NPscan:
    def __init__(self, timeout=3):
        self.timeout = timeout
        self.__data = struct.pack('d', time.time())
        self.__id = os.getpid()
        if self.__id >= 65535: self.__id = 65534
        self.lock = threading.Lock()

    @property
    def __icmpSocket(self):
        Sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        return Sock

    def __inCksum(self, packet):
        if len(packet) & 1:
            packet = packet + '\0'
        words = array.array('h', packet)
        sum = 0
        for word in words:
            sum += (word & 0xffff)
        sum = (sum >> 16) + (sum & 0xffff)
        sum = sum + (sum >> 16)
        return (~sum) & 0xffff

    @property
    def __icmpPacket(self):
        header = struct.pack('bbHHh', 8, 0, 0, self.__id, 0)
        packet = header + self.__data
        chkSum = self.__inCksum(packet)
        header = struct.pack('bbHHh', 8, 0, chkSum, self.__id, 0)
        return header + self.__data

    def mPing(self, ipPool):
        Sock = self.__icmpSocket
        Sock.settimeout(self.timeout)
        packet = self.__icmpPacket
        recvFroms = set()
        sendThr = SendPingThr(ipPool, packet, Sock, self.timeout)
        sendThr.start()
        while True:
            try:
                ac_ip = Sock.recvfrom(1024)[1][0]
                # print(ac_ip)
                if ac_ip not in recvFroms:
                    print("[%s] %s active" % (time_str, ac_ip))
                    recvFroms.add(ac_ip)
            except Exception:
                pass
            finally:
                if not sendThr.isAlive():
                    break
        return recvFroms & ipPool


def get_liveip_list(iplist):
    try:
        s = NPscan()
        ipPool = set(iplist)
        return s.mPing(ipPool)
    except:
        traceback.print_exc()
