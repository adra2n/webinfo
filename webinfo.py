import os.path
from argparse import ArgumentParser
import xlwt as ExcelWrite
import xlrd
from xlutils.copy import copy

from config import result_dir

from modules.burte import domain_burte
from modules.burte import getIP
from modules.burte import path_burte,path_ips_burte
from modules.scan import do_masscan,do_nmap
from modules.attack import do_attack

from utils.print_color import print_color

from libs.json2xls import data2xls
# from libs.json2xls import path_xls
from libs.json2xls import amass_xls

def get_args():

    parser = ArgumentParser()
    parser.add_argument('-d', '--domain',
                        help='需要扫描的域名地址',
                        required=True)
    parser.add_argument('-dm',
                        action='store_true',
                        help="直接进行域名扫描")
    parser.add_argument('-dr',
                        action='store_true',
                        help="进行路径扫描")
    parser.add_argument('-ip',
                        action='store_true',
                        help="提取ip地址")
    parser.add_argument('-ips',
                        action='store_true',
                        help="进行ip地址路径扫描")
    parser.add_argument('-ms',
                        action='store_true',
                        help="进行masscan端口扫描，获取端口开放情况")
    parser.add_argument('-ns',
                        action='store_true',
                        help="进行nmap端口扫描，获取端口服务信息")
    parser.add_argument('-hack',
                        action='store_true',
                        help="进行poc扫描，对端口服务进行漏洞扫描")
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
            domain_burte(args.domain)
            domain_out = os.path.join(result_dir, f"{args.domain}.json")
        print_color("扫描结束", 'g')
        print_color("开始写域名文件", 'i')
        sheet_name = "域名信息"
        name_list = ['name', 'domain', 'ip', 'cidr', 'asn', 'desc', 'tag', 'source']
        try:
            amass_xls(xls,domain_out, csv_out, sheet_name, name_list)
            # print_color('写入 ' + str(count) + ' 行', 'i')
            print_color('域名写入完成', 'g')
        except Exception as e:
            print_color(f"出现错误，错误信息{e},请检查", 'e')

    if args.dr:
        csv_out = os.path.join(result_dir, f"{args.domain}.xls")
        try:
            domain_out = os.path.join(result_dir, f"{args.domain}.json")
            with open(domain_out, 'r') as fh:
                pass
        except:
            print_color("请先运行dm收集域名信息",'e')
            return 0

        workbook = xlrd.open_workbook(csv_out)
        print_color("开始进行路径爆破", "i")
        if args.test:
            path_out=os.path.join(result_dir, f"{args.domain}_path")
        else:
            path_burte(args.domain)
            path_out = os.path.join(result_dir, f"{args.domain}_path")
        print_color("扫描结束", 'g')
        print_color("开始写路径文件", 'i')
        sheet_name = "域名路径信息"
        name_list = ['url', 'status','content-length','title']
        newb = copy(workbook)
        try:
            data2xls(newb,path_out, csv_out, sheet_name, name_list)
            print_color("路径写入成功", 'g')
        except Exception as e:
            print_color(f"出现错误，错误信息{e},请检查", 'e')

    if args.ip:
        try:
            domain_out = os.path.join(result_dir, f"{args.domain}.json")
            with open(domain_out, 'r') as fh:
                pass
        except:
            print_color("请先运行dm收集域名信息",'e')
            return 0
        getIP(args.domain)

    if args.ms:
        try:
            domain_out = os.path.join(result_dir, f"{args.domain}.json")
            with open(domain_out, 'r') as fh:
                pass
        except:
            print_color("请先运行dm收集域名信息", 'e')
            return 0
        do_masscan(args.domain)
        pass

    if args.ips:
        csv_out = os.path.join(result_dir, f"{args.domain}.xls")
        try:
            mass_out = os.path.join(result_dir, f"{args.domain}.masscan")
            with open(mass_out, 'r') as fh:
                pass
        except:
            print_color("请先运行masscan扫描获取开放的端口", 'e')
            return 0
        # getIP(args.domain)
        workbook = xlrd.open_workbook(csv_out)
        print_color("开始进行IP路径爆破", "i")
        if args.test:
            path_out = os.path.join(result_dir, f"{args.domain}_ips_path")
        else:
            path_ips_burte(args.domain)
            path_out = os.path.join(result_dir, f"{args.domain}_ips_path")
        print_color("扫描结束", 'g')
        print_color("开始写路径文件", 'i')
        sheet_name = "IPS路径信息"
        name_list = ['url', 'status', 'length', 'title', 'redirect']
        newb = copy(workbook)
        try:
            path_xls(newb, path_out, csv_out, sheet_name, name_list)
            print_color("路径写入成功", 'g')
        except Exception as e:
            print_color(f"出现错误，错误信息{e},请检查",'e')

    if args.ns:
        try:
            domain_out = os.path.join(result_dir, f"{args.domain}.json")
            with open(domain_out, 'r') as fh:
                pass
        except:
            print_color("请先运行dm收集域名信息", 'e')
            return 0
        try:
            mass_out = os.path.join(result_dir, f"{args.domain}.masscan")
            with open(mass_out, 'r') as fh:
                pass
        except:
            print_color("请先运行masscan扫描获取开放的端口", 'e')
            return 0
        csv_out = os.path.join(result_dir, f"{args.domain}.xls")
        #需要先执行完ms
        if args.test:
            nmap_out = os.path.join(result_dir, f"{args.domain}_nmap")
        else:
            do_nmap(args.domain)
            nmap_out = os.path.join(result_dir, f"{args.domain}_nmap")

        workbook = xlrd.open_workbook(csv_out)
        print_color("开始写nmap文件", 'i')
        sheet_name = "端口信息"
        name_list = ['host', 'port', 'service', 'product','title']
        newb = copy(workbook)
        try:
            data2xls(newb,nmap_out, csv_out, sheet_name, name_list)
            print_color("nmap文件写入成功", 'g')
        except Exception as e:
            print_color(f"出现错误，错误信息{e},请检查", 'e')

    if args.hack:
        try:
            domain_out = os.path.join(result_dir, f"{args.domain}.json")
            with open(domain_out, 'r') as fh:
                pass
        except:
            print_color("请先运行dm收集域名信息", 'e')
            return 0
        try:
            mass_out = os.path.join(result_dir, f"{args.domain}.masscan")
            with open(mass_out, 'r') as fh:
                pass
        except:
            print_color("请先运行masscan扫描获取开放的端口", 'e')
            return 0
        try:
            nmap_out = os.path.join(result_dir, f"{args.domain}.nmap")
            with open(nmap_out, 'r') as fh:
                pass
        except:
            print_color("请先运行nmap扫描获取开放的端口", 'e')
            return 0

        csv_out = os.path.join(result_dir, f"{args.domain}.xls")
        # 需要先执行完ms
        # workbook = xlrd.open_workbook(csv_out)
        do_attack(args.domain)
        poc_out=os.path.join(result_dir, f"{args.domain}_hack")
        workbook = xlrd.open_workbook(csv_out)
        print_color("开始写hack文件", 'i')
        sheet_name = "漏洞信息"
        name_list = ['host', 'port', 'service', 'level', 'vul']
        newb = copy(workbook)
        try:
            data2xls(newb, poc_out, csv_out, sheet_name, name_list)
            print_color("漏洞文件写入成功", 'g')
        except Exception as e:
            print_color(f"出现错误，错误信息{e},请检查", 'e')


if __name__ == "__main__":
    main()
