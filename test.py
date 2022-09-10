# from config import dirscan
# import os
# cmd =f"python {dirscan} -i 200,500,403 --exclude-texts 'Not found', 'Error' --min-response-size 500 --exclude-response 404.html -u api.boss.mgp.mi.com -o test --format json"
# os.system(cmd)


# ip_list=ip.split('.')
# i=int(ip_list[3])
# if i-32 < 0:
#     start=0
# else:
#     start=i-32
# if i+32 > 254:
#     end=254
# else:
#     end=i+32
#
# for j in range(start,end):
#     ip=ip_list[0]+'.'+ip_list[1]+"."+ip_list[2]+'.'+str(j)
#     print(ip)
from multiprocessing.resource_tracker import main
main(11)