import traceback

import os
from config import result_dir,ports
import threading
import queue
from multiprocessing.dummy import Pool as threadpool
from libnmap.parser import NmapParser, NmapParserException
from libnmap.process import NmapProcess
from utils.print_color import print_color
from utils.get_info import get_info

lock = threading.Lock()
import subprocess
import json

# global nmap_out

def do_masscan(domain):
    mass_out = os.path.join(result_dir, f"{domain}_masscan")
    ips_in = os.path.join(result_dir, f"{domain}_ips")
    masscan_start_command = f'masscan --ports {ports} --rate=1000 -iL {ips_in} -oJ {mass_out} --append-output'
    # p3 = subprocess.Popen([masscan_start_command], shell=True)
    os.system(masscan_start_command)
    # p3.wait()


def pre_nmap(domain):
    Q = queue.Queue()
    mass_out = os.path.join(result_dir, f"{domain}_masscan")
    with open(mass_out) as f:
        lines = f.readlines()
        curr = lines[1:]
        curr = curr[:-1]
        for eachline in curr:
            line = eachline.strip().strip(',')
            if line:
                try:
                    js = json.loads(line)
                    ip = str(js['ip'])  # 这里读取的i平时unicode类型的。
                    port = js['ports'][0]['port']
                    check_ip = {
                        "ip": ip,
                        "port": port
                    }
                    Q.put(check_ip)
                except:
                    traceback.print_exc()
        return Q


def nmap_doscan(item,nmap_out):
    print_color(f'正在扫描{item}','i')
    item_host = item['ip']
    item_port = item['port']
    nmproc = NmapProcess(
        item_host,
        f'-sV -T4 --open --script=banner -p {item_port}')
    rc = nmproc.run()
    if rc != 0:
        print_color(f"{item_host} 扫描出现错误",'e')
    else:
        # print(nmproc.stdout)
        parsed = NmapParser.parse(str(nmproc.stdout))  # 需要是字符串类型
        # print(parsed.hosts[0].services)
        with open(nmap_out, "a") as f:
            for host in parsed.hosts:
                for serv in host.services:
                    if str(serv.service).lower() == "tcpwrapped":
                        pass
                    else:
                        if serv.service =="http":
                            url=f"http://{host.address}:{str(serv.port)}"
                            _,_,title=get_info(url)
                        else:
                            title=""

                        data = {
                            "host": host.address,
                            "port": str(serv.port),
                            "service": serv.service,
                            "product": serv.banner,
                            "title":title,
                        }

                        f.writelines(json.dumps(data,ensure_ascii=False))
                        f.writelines("\n")
                        print_color(f"{data}写入成功",'g')


def do_nmap(domain):
    Q = pre_nmap(domain)
    p = threadpool(100)
    nmap_out = os.path.join(result_dir, f"{domain}_nmap")
    while not Q.empty():
        item = Q.get()
        # nmap_doscan(item)
        p.apply_async(nmap_doscan, args=(item,nmap_out,))
    p.close()
    p.join()
    # return nmap_out




