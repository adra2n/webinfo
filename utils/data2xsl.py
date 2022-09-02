import json
import os
from config import result_dir
import xlrd
import xlwt as ExcelWrite

def data2xls(xls,data_in,csv_out,sheet_name,name_list):
    sheet = xls.add_sheet(sheet_name)
    for i in name_list:
        sheet.write(0, name_list.index(i), i)

    data=[]
    with open(data_in) as f:
        for line in f:
            data.append(json.loads(line))

    for j, row in enumerate(data):
        for i in range(len(name_list)):
            # print(name_list[i])
            # print(row[name_list[i]])
            try:
                sheet.write(j + 1, i, row[name_list[i]])
            except:
                pass

    xls.save(csv_out)
        # print(row[sheet_name[j]])


    #     try:
    #         sheet.write(i + 1, 0, host)
    #         sheet.write(i + 1, 1, port)
    #         sheet.write(i + 1, 2, service)
    #         sheet.write(i + 1, 3, product)
    #         sheet.write(i + 1, 4, title)
    #     except:
    #         pass
    #
    # xls.save(csv_out)
# xls = ExcelWrite.Workbook()
# csv_out = os.path.join(result_dir, "test.xls")
# name_list = ['host', 'port', 'service', 'product','title']
# # workbook = xlrd.open_workbook(csv_out)
# sheet_name= 'test'
# data_in = os.path.join(result_dir, f"netease.com_nmap")
# data2xls(xls,data_in,sheet_name,name_list)
