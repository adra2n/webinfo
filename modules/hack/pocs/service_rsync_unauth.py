# __author__ = 'gaohe'
# -*- coding:utf-8 -*-
from subprocess import *
import json
import time
import sys
import os
import stat

# print passwords


class rsync_test:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        # os.chmod(passwords, stat.S_IRUSR + stat.S_IWUSR)

    def runtime(self, cmd, timeout=2):
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        t_beginning = time.time()
        seconds_passed = 0
        while True:
            if proc.poll() is not None:
                res = proc.communicate()
                exitcode = proc.poll() if proc.poll() else 0
                return res, exitcode
            seconds_passed = time.time() - t_beginning
            if timeout and seconds_passed > timeout:
                proc.terminate()
                out, exitcode = '', 128
                return out, exitcode
            time.sleep(0.1)

    def check(self):
        command = 'rsync --timeout=1 --port={port} {ip}::'.format(port=self.port, ip=self.ip)
        # print command
        modules = []

        # p = subprocess.Popen(
        #     [command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            out, code = self.runtime(cmd=command)
            # print out, code
            if code == 0:
                for i in out:
                    module = i.split('\t')[0]
                    command = 'rsync --timeout=1 --port={port} {ip}::{module}'.format(
                        port=self.port,
                        ip=self.ip,
                        module=module)
                    # print command
                    out2, code = self.runtime(cmd=command)
                    # print out2, code
                    if code == 0:
                        # data = out
                        if len(out2) and module:
                            modules.append(module.strip())

                            row = {
                                "wakaka": "ok",
                                'level': "High",
                                "vul": "Rsync Modules:{modules} 未授权访问".format(
                                    modules=modules)
                            }
                            print(row)
                        else:
                            pass
                    else:
                        pass
            else:
                pass
        except Exception as e:
            print(e)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        rs = rsync_test(ip, port)
        rs.check()
