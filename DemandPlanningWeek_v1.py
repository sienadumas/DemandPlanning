# Sasha Babayan
# 9/27/2015

import csv
import datetime

# data is a dictionary: item# -> date -> totalOrders
def read_csv_data(file_name):
    input_file = csv.DictReader(open(file_name))
    data = dict([])
    for row in input_file:
        item_num = int(row["Item #"].replace(",",""))
        raw_date = row["Invoice Date"].split("/")
        date = datetime.date(int(raw_date[2]), int(raw_date[0]), int(raw_date[1]))
        amnt = float(row["Requested Quantity"].replace(",",""))
        if item_num in data.keys():
            if date in data[item_num].keys():
                data[item_num][date] += amnt
            else:
                data[item_num][date] = amnt
        else:
            data[item_num] = dict([])
            data[item_num][date] = amnt
    return data

d = read_csv_data("C:\Users\Sasha\Dropbox\PlumShipment\Plum_OrderData.csv")
print d[866]
