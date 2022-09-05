from config import amass_bin
import os
import traceback
from config import result_dir
from utils.cmder import subExec


def domain_burte(domain):
    domain_out = os.path.join(result_dir, f"{domain}.json")
    try:
        amass_cmd = f"{amass_bin} enum -v -src -ip -brute -min-for-recursive 2 -d {domain} -json {domain_out}"
        os.system(amass_cmd)
    except Exception as e:
        traceback.print_exc()

    # return domain_out

