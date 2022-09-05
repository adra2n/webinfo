# webinfo

> 现在命令提醒还不完善，需要先执行-dm，在执行其他的，-ms、-ns需要先执行-ip，-poc需要先执行-ns

一款自动化收集信息的工具，已经完成以下功能：
```
usage: main.py [-h] -d DOMAIN [-dm] [-dr] [-ip] [-ms] [-ns] [-poc] [--test]

optional arguments:
  -h, --help            show this help message and exit
  -d DOMAIN, --domain DOMAIN
                        需要扫描的域名地址
  -dm                   直接进行域名扫描
  -dr                   进行路径扫描
  -ip                   提取ip地址
  -ms                   进行masscan端口扫描，获取端口开放情况
  -ns                   进行nmap端口扫描，获取端口服务信息
  -poc                  进行poc扫描，对端口服务进行漏洞扫描
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

[X] 将写入excel写成统一调用

[X] 优化命令行提醒

[ ] 集成nuclei进行漏洞扫描

[ ] 集成天眼查，获取子公司信息

[ ] 集成fofa增加信息收集途径

### 2022年9月5日

[+] 新增了对masscan判断出存活的ip的路径扫描 

[+] 舍弃dirsearch，更改为自己的路径爆破脚本

[ ] 需要对路径扫描结果进行进一步处理，排除掉title为空的、默认title的，如"welcome to tengine!"等

[ ] 对路径的扫描结果进行处理，一个路径扫描出20多个路径返回200，就是存在问题，直接舍弃掉





