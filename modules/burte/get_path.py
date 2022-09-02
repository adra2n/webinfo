from config import dirscan
import os
import traceback
from json import loads as json_loads
from config import result_dir,path_dict,threadNum


def path_burte(domain):
    amass_in = os.path.join(result_dir, f"{domain}.json")
    path_out = os.path.join(result_dir, f"{domain}_path")
    dir_in = os.path.join(result_dir, f"{domain}_host")

    with open(dir_in, 'a') as fd:
        with open(amass_in, 'r') as fh:
            for line in fh:
                data = json_loads(line)
                host = data['name']
                fd.writelines(host)
                fd.writelines('\n')

    try:
        cmd = f"python {dirscan} -x 301,302,403,404,405,500,501,502,503 --exclude-texts 'Not found', 'Error' " \
              f"--min-response-size 500 --exclude-response 404.html " \
              f"-l {dir_in} -w {path_dict} " \
              f"-o {path_out} --format json " \
              f"-t {threadNum}"
        os.system(cmd)
    except Exception as e:
        traceback.print_exc()

    return path_out
