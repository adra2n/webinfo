from config import amass_bin
from config import ip_count
from IPy import IP
import os
import traceback
import threading
from json import loads as json_loads
from config import result_dir, path_dict
import queue
from multiprocessing.dummy import Pool as threadpool
import requests
import json
from utils.get_info import get_info
from utils.print_color import print_color
from libs.httplibs import requests_headers

lock = threading.Lock()


def domain_burte(domain):
    domain_out = os.path.join(result_dir, f"{domain}.json")
    try:
        amass_cmd = f"{amass_bin} enum -v -src -ip -brute -min-for-recursive 2 -d {domain} -json {domain_out}"
        os.system(amass_cmd)
    except Exception as e:
        traceback.print_exc()

def getIP(domain):
    ip_set = []
    amass_in = os.path.join(result_dir, f"{domain}.json")
    ips_in = os.path.join(result_dir, f"{domain}_ips")

    with open(amass_in, 'r') as fh:
        for line in fh:
            data = json_loads(line)
            addresses = data['addresses']
            for i, row in enumerate(addresses):
                ip = row['ip']
                if IP(ip).version() == 4 and IP(ip).iptype() == "PUBLIC":
                    ip_list = ip.split('.')
                    ip3 = ip_list[0] + '.' + ip_list[1] + "." + ip_list[2]
                    if ip3 not in ip_set:
                        ip_set.append(ip3)

                    j = int(ip_list[3])
                    if j - ip_count < 0:
                        start = 0
                    else:
                        start = j - ip_count
                    if j + ip_count > 254:
                        end = 254
                    else:
                        end = j + ip_count

    with open(ips_in, 'a') as fd:
        for ip3 in ip_set:
            for k in range(start, end):
                ip4 = ip3 + '.' + str(k)
                fd.writelines(ip4)
                fd.writelines('\n')


def check(item, path_out):
    print_color(f"正在扫描{item}", 'i')
    try:
        req = requests.get(item, headers=requests_headers(),timeout=3, verify=False, allow_redirects=False)
        if req.status_code not in [301, 302, 403, 404, 405, 500, 501, 502, 503] and len(req.content)>500:
            _,_,title = get_info(req.url)
            res = {
                "content-length": len(req.content),
                "status": req.status_code,
                "url": req.url,
                "title": title
            }
            with open(path_out, 'a') as fd:
                lock.acquire()
                fd.writelines(json.dumps(res, ensure_ascii=False))
                fd.writelines("\n")
                lock.release()

    except Exception as e:
        # traceback.print_exc()
        pass

def path_burte(domain):
    Q = queue.Queue()
    amass_in = os.path.join(result_dir, f"{domain}.json")
    path_out = os.path.join(result_dir, f"{domain}_path")

    with open(amass_in, 'r') as fh:
        with open(path_dict, 'r') as f:
            for line in fh:
                data = json_loads(line)
                host = data['name'].strip()
                test_url = f"https://{host}/noexit_path"
                try:
                    test_r = requests.get(test_url, headers=requests_headers(), timeout=2, verify=False)
                    if test_r.status_code == 200 or test_r.status_code == 500 or test_r.status_code == 403:
                        print_color(f"{test_url}，返回值{test_r.status_code}，跳过扫描",'i')
                    else:
                        print_color(f"{test_url}，返回值{test_r.status_code}，开始扫描", 'i')
                        lines = f.readlines()
                        for item in lines:
                            url = f"https://{host}/{item.strip()}"
                            Q.put(url)
                except:
                    pass

                p = threadpool(100)
                while not Q.empty():
                    item = Q.get()
                    # print(item)
                    p.apply_async(check, args=(item, path_out,))
                p.close()
                p.join()


def path_ips_burte(domain):
    Q = queue.Queue()
    # amass_in = os.small_path.join(result_dir, f"{domain}.json")
    path_out = os.path.join(result_dir, f"{domain}_ips_path")
    mass_out = os.path.join(result_dir, f"{domain}_masscan")
    # ips_in = os.path.join(result_dir, f"{domain}_ips")

    # with open(ips_in, 'a') as fd:

    with open(mass_out) as f:
        with open(path_dict, 'r') as fp:
            lines = f.readlines()
            curr = lines[1:]
            curr = curr[:-1]
            for eachline in curr:
                line = eachline.strip().strip(',')
                if line:
                    js = json_loads(line)
                    ip = str(js['ip'])  # 这里读取的i平时unicode类型的。
                    port = js['ports'][0]['port']
                    host = f"{ip}:{port}"
                    if int(port) in [443,8443]:
                        sc="https"
                    else:
                        sc="http"
                    test_url = f"{sc}://{host}/noexit_path"
                    try:
                        test_r = requests.get(test_url, headers=requests_headers(), timeout=2, verify=False)
                        if test_r.status_code == 200 or test_r.status_code == 500 or test_r.status_code == 403:
                            print_color(f"{host}，返回值{test_r.status_code},跳过扫描",'i')
                        else:
                            print_color(f"{test_url}，返回值{test_r.status_code}，开始扫描", 'i')
                            lines = fp.readlines()
                            for item in lines:
                                url = f"{sc}://{host}/{item.strip()}"
                                Q.put(url)
                    except:
                        # print_color(f"{test_url} 无法连接，跳过扫描", 'i')
                        pass
                    # Q.put(host)

                    p = threadpool(100)
                    while not Q.empty():
                        item = Q.get()
                        p.apply_async(check, args=(item, path_out,))
                    p.close()
                    p.join()
