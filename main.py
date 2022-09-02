import os.path
import traceback
from argparse import ArgumentParser
from config import result_dir
from modules.burte.get_domains import domain_burte
from modules.burte.get_ip import getIP
from modules.burte.get_path import path_burte
from utils.print_color import print_color
import xlwt as ExcelWrite
import xlrd
from xlutils.copy import copy
from modules.scan.scan import do_masscan,do_nmap
from modules.hack.poc_attack import do_attack
from utils.data2xsl import data2xls

def get_args():
    parser = ArgumentParser()
    parser.add_argument('-d', '--domain',
                        help='需要扫描的域名地址',
                        required=True)
    parser.add_argument('-dm',
                        action='store_true',
                        help="是否直接进行域名扫描，默认为false")
    parser.add_argument('-dr',
                        action='store_true',
                        help="是否直接进行路径扫描，默认为false")
    parser.add_argument('-ip',
                        action='store_true',
                        help="提取ip地址，默认为false")
    parser.add_argument('-ms',
                        action='store_true',
                        help="进行masscan端口扫描，获取端口开放情况，默认为false")
    parser.add_argument('-ns',
                        action='store_true',
                        help="进行nmap端口扫描，获取端口服务信息，默认为false")
    parser.add_argument('-poc',
                        action='store_true',
                        help="进行poc扫描，对端口服务进行漏洞扫描，默认为false")
    parser.add_argument('--test',
                        action='store_true',
                        help="测试，默认为false")

    return parser


def main():
    xls = ExcelWrite.Workbook()
    args = get_args().parse_args()

    # print(csv_out)

    if args.dm:
        csv_out = os.path.join(result_dir, f"{args.domain}.xls")
        print_color("开始进行domain扫描", 'i')
        if args.test:
            domain_out = os.path.join(result_dir, f"{args.domain}.json")
        else:
            domain_out = domain_burte(args.domain)

        print_color("扫描结束", 'g')
        print_color("开始写域名文件", 'i')
        sheet_name = "域名信息"
        name_list = ['name', 'domain', 'ip', 'cidr', 'asn', 'desc', 'tag', 'source']
        count = data2xls(xls,domain_out, csv_out, sheet_name, name_list)
        print_color('写入 ' + str(count) + ' 行', 'i')
        print_color('域名写入完成', 'g')

    if args.dr:
        csv_out = os.path.join(result_dir, f"{args.domain}.xls")
        try:
            workbook = xlrd.open_workbook(csv_out)
            print_color("开始进行路径爆破", "i")
            if args.test:
                path_out=os.path.join(result_dir, f"{args.domain}_path")
            else:
                path_out=path_burte(args.domain)
            print_color("扫描结束", 'g')
            print_color("开始写路径文件", 'i')
            sheet_name = "路径信息"
            name_list = ['url', 'status','length','title','redirect']
            newb = copy(workbook)
            data2xls(newb,path_out, csv_out, sheet_name, name_list)
            print_color("路径写入成功", 'g')
        except:
            traceback.print_exc()
            print_color("请先运行dm获取域名",'e')

    if args.ip:
        # w无需写如excel中
        getIP(args.domain)

    if args.ms:
        # 需要先执行ip
        do_masscan(args.domain)
        pass

    if args.ns:
        csv_out = os.path.join(result_dir, f"{args.domain}.xls")
        #需要先执行完ms
        if args.test:
            nmap_out = os.path.join(result_dir, f"{args.domain}_nmap")
        else:
            nmap_out=do_nmap(args.domain)

        workbook = xlrd.open_workbook(csv_out)
        print_color("开始写nmap文件", 'i')
        sheet_name = "端口信息"
        name_list = ['host', 'port', 'service', 'product','title']
        newb = copy(workbook)
        try:
            data2xls(newb,nmap_out, csv_out, sheet_name, name_list)
            print_color("nmap文件写入成功", 'g')
        except:
            print_color("已存在表名称，请手工删除",'e')

    if args.poc:
        csv_out = os.path.join(result_dir, f"{args.domain}.xls")
        # 需要先执行完ms
        # workbook = xlrd.open_workbook(csv_out)
        poc_out = do_attack(args.domain)
        workbook = xlrd.open_workbook(csv_out)
        print_color("开始写hack文件", 'i')
        sheet_name = "漏洞信息"
        name_list = ['host', 'port', 'service', 'level', 'vul']
        newb = copy(workbook)
        data2xls(newb, poc_out, csv_out, sheet_name, name_list)
        print_color("漏洞文件写入成功", 'g')


if __name__ == "__main__":
    main()
