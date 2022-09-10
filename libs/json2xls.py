import json
import traceback
from json import loads as json_loads


def amass_xls(xls,amass_in, csv_out,sheet_name,name_list):
    sheet = xls.add_sheet(sheet_name)
    for i in name_list:
        sheet.write(0, name_list.index(i), i)

    amass = []

    with open(amass_in, 'r') as fh:
        for line in fh:
            amass.append(json_loads(line))

    write_count = 0
    for i, row in enumerate(amass):
        # print(row)
        name = row['name']
        domain = row['domain']
        addresses = row['addresses']
        ip = []
        cidr = []
        asn = []
        desc = []
        tag = ''
        source = []

        for address in addresses:
            ip.append(address['ip'])
            cidr.append(address['cidr'])
            asn.append(str(address['asn']))
            desc.append(address['desc'])

        tag = row['tag']

        if 'sources' in row:
            source = row['sources']
        elif 'source' in row:
            source.append(row['source'])
        try:
            for j, d in enumerate(ip):

                sheet.write(i + j + 1, 0, name)
                sheet.write(i + j + 1, 1, domain)
                sheet.write(i + j + 1, 2, d)
                sheet.write(i + j + 1, 3, cidr[j])
                sheet.write(i + j + 1, 4, asn[j])
                sheet.write(i + j + 1, 5, desc[j])
                sheet.write(i + j + 1, 6, tag)
                sheet.write(i + j + 1, 7, source[0])
                write_count= write_count+i+j
        except:
            # traceback.print_exc()
            pass
    # print(amass)

    xls.save(csv_out)


# def path_xls(xls,path_in, csv_out,sheet_name,name_list):
#     sheet = xls.add_sheet(sheet_name)
#     for i in name_list:
#         sheet.write(0, name_list.index(i), i)
#
#     data=[]
#     with open(path_in, 'r') as fh:
#         lines = fh.readlines()
#         for eachline in lines:
#             row = json_loads(eachline)
#             data.append(row)
#
#     for j, row in enumerate(data):
#         try:
#             url = row['url']
#             status = row['status']
#             content_length = row['content-length']
#             title=row['title']
#             # redirect = row['redirect']
#             try:
#                 sheet.write(j+1, 0, url)
#                 sheet.write(j+1, 1, status)
#                 sheet.write(j+1, 2, content_length)
#                 sheet.write(j+1, 3, title)
#             except:
#                 traceback.print_exc()
#         except:
#             traceback.print_exc()
#             pass
#     xls.save(csv_out)

### 没有特殊json格式的可以采用一下函数写excel

def data2xls(xls,data_in,csv_out,sheet_name,name_list):
    sheet = xls.add_sheet(sheet_name)
    for i in name_list:
        sheet.write(0, name_list.index(i), i)

    data=[]
    with open(data_in) as f:
        for line in f:
            data.append(json_loads(line))

    for j, row in enumerate(data):
        for i in range(len(name_list)):
            # print(name_list[i])
            # print(row[name_list[i]])
            try:
                sheet.write(j + 1, i, row[name_list[i]])
            except:
                pass

    xls.save(csv_out)