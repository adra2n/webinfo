from config import amass_bin
from config import ip_count
from IPy import IP
import os
import traceback
from json import loads as json_loads
from config import result_dir, path_dict
import queue
from multiprocessing.dummy import Pool as threadpool
import requests
import json
from utils.get_title import gettitle
from utils.print_color import print_color


def domain_burte(domain):
    domain_out = os.path.join(result_dir, f"{domain}.json")
    try:
        amass_cmd = f"{amass_bin} enum -v -src -ip -brute -min-for-recursive 2 -d {domain} -json {domain_out}"
        os.system(amass_cmd)
    except Exception as e:
        traceback.print_exc()

    # return domain_out


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
    check_url = f"http://{item}/"
    print_color(f"正在扫描{check_url}", 'i')
    test_url = check_url + "sadsadasdasdasdasdasasd"
    try:
        test_r = requests.get(test_url, timeout=2, verify=False)
        if test_r.status_code == 200 or test_r.status_code == 500:
            pass
        else:
            with open(path_out, 'a') as fd:
                with open(path_dict, 'r') as f:
                    lines = f.readlines()
                    for item in lines:
                        url = check_url + item.strip()

                        try:
                            req = requests.get(url, timeout=3, verify=False, allow_redirects=False)
                            if req.status_code not in [301, 302, 403, 404, 405, 500, 501, 502, 503] and len(req.content)>200:
                                res = {
                                    "content-length": len(req.content),
                                    "status": req.status_code,
                                    "url": req.url,
                                    "title": gettitle(req.url)
                                }
                                fd.writelines(json.dumps(res, ensure_ascii=False))
                                fd.writelines("\n")

                        except Exception as e:
                            # traceback.print_exc()
                            pass
                        # print(e)

    except:
        # traceback.print_exc()
        pass


def path_burte(domain):
    Q = queue.Queue()
    amass_in = os.path.join(result_dir, f"{domain}.json")
    path_out = os.path.join(result_dir, f"{domain}_path")
    # dir_in = os.path.join(result_dir, f"{domain}_host")

    # with open(dir_in, 'a') as fd:
    with open(amass_in, 'r') as fh:
        for line in fh:
            data = json_loads(line)
            host = data['name']
            # print(host)
            Q.put(host)

    p = threadpool(100)
    while not Q.empty():
        item = Q.get()
        # print(item)
        p.apply_async(check, args=(item, path_out,))
    p.close()
    p.join()
    # fd.writelines(host)
    # fd.writelines('\n')

    # try:
    #     cmd = f"python {dirscan} -x 301,302,403,404,405,500,501,502,503 --exclude-texts 'Not found', 'Error' " \
    #           f"--min-response-size 500 --exclude-response 404.html " \
    #           f"-l {dir_in} -w {path_dict} " \
    #           f"-o {path_out} --format json " \
    #           f"-t {threadNum}"
    #     os.system(cmd)
    # except Exception as e:
    #     traceback.print_exc()

    # return path_out


def path_ips_burte(domain):
    Q = queue.Queue()
    # amass_in = os.small_path.join(result_dir, f"{domain}.json")
    path_out = os.path.join(result_dir, f"{domain}_ips_path")
    mass_out = os.path.join(result_dir, f"{domain}_masscan")
    # ips_in = os.path.join(result_dir, f"{domain}_ips")

    # with open(ips_in, 'a') as fd:
    with open(mass_out) as f:
        lines = f.readlines()
        curr = lines[1:]
        curr = curr[:-1]
        for eachline in curr:
            line = eachline.strip().strip(',')
            if line:
                try:
                    js = json_loads(line)
                    ip = str(js['ip'])  # 这里读取的i平时unicode类型的。
                    port = js['ports'][0]['port']
                    host = f"{ip}:{port}"
                    Q.put(host)
                except:
                    traceback.print_exc()

    p = threadpool(100)
    while not Q.empty():
        item = Q.get()
        p.apply_async(check, args=(item, path_out,))
    p.close()
    p.join()
    # try:
    #     cmd = f"python {dirscan} -x 301,302,403,404,405,500,501,502,503 --exclude-texts 'Not found', 'Error' " \
    #           f"--min-response-size 500 --exclude-response 404.html " \
    #           f"-l {ips_in} -w {path_dict} " \
    #           f"-o {path_out} --format json " \
    #           f"-t {threadNum}"
    #     os.system(cmd)
    # except Exception as e:
    #     traceback.print_exc()
