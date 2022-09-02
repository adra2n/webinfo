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
    return write_count
