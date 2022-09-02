import json


def nmap_xls(xls,nmap_out, csv_out,sheet_name,name_list):
    sheet = xls.add_sheet(sheet_name)
    for i in name_list:
        sheet.write(0, name_list.index(i), i)

    data=[]
    with open(nmap_out) as f:
        for line in f:
            data.append(json.loads(line))

    for i, row in enumerate(data):
        # print(row)
        host = row['host']
        port = row['port']
        service = row['service']
        product = row['product']
        title= row['title']

        try:
            sheet.write(i + 1, 0, host)
            sheet.write(i + 1, 1, port)
            sheet.write(i + 1, 2, service)
            sheet.write(i + 1, 3, product)
            sheet.write(i + 1, 4, title)
        except:
            pass

    xls.save(csv_out)

