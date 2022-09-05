from config import result_dir
from json import loads as json_loads
from config import ip_count
from IPy import IP
import os


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
                if IP(ip).version() == 4 and IP(ip).iptype()=="PUBLIC":
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