# Sasha Babayan
# 9/27/2015

import csv
import datetime

def main():
    cycle = 6*7
    pastOrders = read_csv_data("Plum_OrderData.csv")
    #pastOrders = read_csv_data("C:\Users\Sasha\Dropbox\PlumShipment\Plum_OrderData.csv")
    omega(cycle, pastOrders[866])

# omega gets the historical maximum
# n is the time period (consecutive number of weeks)
# totalOrders is a dictionary from date to totalOrders (for a specific item)
def omega(n, totalOrders):
    # sort the dates
    dates = totalOrders.keys()
    dates.sort()
    
    max_order = 0
    max_start_date = None

    for i in range(len(dates)):
        start = dates[i]
        # current_order = 0
        date = start
        # print start+datetime.timedelta(days=n)
        curr = i
        current_order = 0
        while (curr+1 < len(dates)) and (dates[curr] < start + datetime.timedelta(days=n)):
            current_order += totalOrders[dates[curr]]
            curr += 1
            #if start == datetime.date(2014, 06, 14):
             #   print 'date: ' + str(date) + ', total: ' + str(totalOrders[date])
              #  print current_order
        if current_order > max_order:
            max_order = current_order
            max_start_date = start
  #  print max_order
  #  print max_start_date
  #  print max_start_date + datetime.timedelta(days=n-1)
    return (max_start_date, max_order)




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

if __name__ == "__main__":
    main()