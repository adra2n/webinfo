import json
from utils.print_color import print_color

def poc_xls(xls,poc_out, csv_out,sheet_name,name_list):
    sheet = xls.add_sheet(sheet_name)
    for i in name_list:
        sheet.write(0, name_list.index(i), i)

    try:
        data=[]
        with open(poc_out) as f:
            for line in f:
                data.append(json.loads(line))

        for i, row in enumerate(data):
            # print(row)
            host = row['host']
            port = row['port']
            service = row['service']
            level = row['level']
            vul= row['vul']

            try:
                sheet.write(i + 1, 0, host)
                sheet.write(i + 1, 1, port)
                sheet.write(i + 1, 2, service)
                sheet.write(i + 1, 3, level)
                sheet.write(i + 1, 4, vul)
            except:
                pass
    except:
        print_color("没有发现漏洞",'e')
    try:
        xls.save(csv_out)
    except:
        print_color("已存在sheet表，请手工删除",'e')

