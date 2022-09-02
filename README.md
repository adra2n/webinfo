# webinfo

一款自动化收集信息的工具，已经完成以下功能：
```
usage: main.py [-h] -d DOMAIN [-dm] [-dr] [-ip] [-ms] [-ns] [-poc] [--test]

optional arguments:
  -h, --help            show this help message and exit
  -d DOMAIN, --domain DOMAIN
                        需要扫描的域名地址
  -dm                   是否直接进行域名扫描，默认为false
  -dr                   是否直接进行路径扫描，默认为false
  -ip                   提取ip地址，默认为false
  -ms                   进行masscan端口扫描，获取端口开放情况，默认为false
  -ns                   进行nmap端口扫描，获取端口服务信息，默认为false
  -poc                  进行poc扫描，对端口服务进行漏洞扫描，默认为false
  --test                测试，默认为false
```

- 其中扫描子域名调用了amass进行的
- 扫描路径信息借助了dirsearch进行，速度较慢，其中自定义了字典，加快速度
- poc扫描框架是自己写的，poc在pocs目录下面，后续考虑集成nuclei扫描

- 扫描结果写入result目录中，舍弃了数据库，直接写入文件
- 所有数据均写入excel中，便于结果的查看及数据保存

写过不少程序，不断增加数据库、缓存、分布式、UI界面越写越大

在某次活动中，听到一句话"渗透工作的80%是信息收集"，想想没必要做的那么复杂，只要能把信息搞出来

其他都不重要

结构现在还比较乱，不过可以正常运行了，只要一个domain输入，其他就不用管了，看excel即可

TODO:

[ ] 将写入excel写成统一调用

[ ] 集成nuclei进行漏洞扫描

[ ] 集成天眼查，获取子公司信息

[ ] 集成fofa增加信息收集途径





