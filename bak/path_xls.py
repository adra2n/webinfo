import json
from utils.get_title import gettitle
import urllib3
urllib3.disable_warnings()


def path_xls(xls,path_in, csv_out,sheet_name,name_list):
    sheet = xls.add_sheet(sheet_name)
    for i in name_list:
        sheet.write(0, name_list.index(i), i)
    with open(path_in, 'r') as fh:
        row_data=json.load(fh)
    # print(row_data['results'])
    for i,row in enumerate(row_data['results']):
        url = row['url']
        status = row['status']
        content_length = row['content-length']
        title=gettitle(url)
        redirect = row['redirect']
        try:
            sheet.write(i+1, 0, url)
            sheet.write(i+1, 1, status)
            sheet.write(i+1, 2, content_length)
            sheet.write(i+1, 3, title)
            sheet.write(i+1, 4, redirect)
        except:
            pass

    xls.save(csv_out)


    # write_count = 0
    # for i, row in enumerate(amass):
    #     name = row['name']
    #     domain = row['domain']
    #     addresses = row['addresses']
    #     ip = []
    #     cidr = []
    #     asn = []
    #     desc = []
    #     tag = ''
    #     source = []
    #
    #     for address in addresses:
    #         ip.append(address['ip'])
    #         cidr.append(address['cidr'])
    #         asn.append(str(address['asn']))
    #         desc.append(address['desc'])
    #
    #     tag = row['tag']
    #
    #     if 'sources' in row:
    #         source = row['sources']
    #     elif 'source' in row:
    #         source.append(row['source'])
    #
    #     for j, d in enumerate(ip):
    #         sheet.write(i + j + 1, 0, name)
    #         sheet.write(i + j + 1, 1, domain)
    #         sheet.write(i + j + 1, 2, d)
    #         sheet.write(i + j + 1, 3, cidr[j])
    #         sheet.write(i + j + 1, 4, asn[j])
    #         sheet.write(i + j + 1, 5, desc[j])
    #         sheet.write(i + j + 1, 6, tag)
    #         sheet.write(i + j + 1, 7, source[0])
    #         write_count= write_count+i+j
    #
    # # print(amass)
    #
    # xls.save(csv_out)
    # return write_count
