import os
import platform

currentdir = os.path.abspath(os.path.dirname(__file__))
# print(currentdir)

if platform.system() == "Darwin":
    amass_bin = os.path.abspath(os.path.join(currentdir, "bin/amass_mac"))
elif platform.system() == "Linux":
    amass_bin = os.path.abspath(os.path.join(currentdir, "bin/amass_linux"))

dirscan = os.path.abspath(os.path.join(currentdir, 'modules/burte/dirsearch/dirsearch.py'))
path_dict = os.path.abspath(os.path.join(currentdir, 'dicts/path'))
result_dir = os.path.join(currentdir, "result")
poc_dir = os.path.abspath(os.path.join(currentdir, 'modules/hack/pocs'))

ip_count=5
threadNum=50
