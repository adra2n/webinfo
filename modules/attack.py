from config import result_dir, poc_dir
from multiprocessing.dummy import Pool as threadpool
import os
import json
import queue
from utils.print_color import print_color
from utils.cmder import subExec


def poc_run(item_list, result_out):
    js = item_list
    host = str(js['host'])
    port = str(js['port'])
    service = str(js['service'])
    banner = str(js['product'])
    # print_color(f"正在测试{item_list}",'i')
    for pocfile in os.listdir(poc_dir):
        # print(pocfile)
        cmdLine = f'python {poc_dir}/{pocfile} {host} {port}'
        print_color(f'正在测试{cmdLine}', 'i')
        data = subExec(cmdLine)
        if 'wakaka' in data:
            data = eval(data)
            result = {
                "host": host,
                "port": port,
                "service": service,
                "level": data['level'],
                "vul": data['vul']
            }
            with open(result_out, "a") as f:
                f.writelines(json.dumps(result, ensure_ascii=False))
                f.writelines("\n")


def do_attack(domain):
    Q = queue.Queue()
    nmap_out = os.path.join(result_dir, f"{domain}_nmap")
    result_out = os.path.join(result_dir, f"{domain}_hack")
    with open(nmap_out) as f:
        lines = f.readlines()
        for eachline in lines:
            line = eachline.strip().strip(',')
            js = json.loads(line)
            Q.put(js)

    p2 = threadpool(10)
    while not Q.empty():
        l = Q.get()
        p2.apply_async(poc_run, args=(l, result_out,))
    p2.close()
    p2.join()

    # return result_out
