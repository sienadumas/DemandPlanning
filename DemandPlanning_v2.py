# Sasha Babayan
# 9/27/2015

import csv
import datetime

def main():
    cycle = 60
    target = 72000
    pastOrders = read_csv_data("Plum_OrderData.csv")

    train, test = split_data(866, pastOrders, 90)
    train_dates, test_dates = sorted(train.keys()), sorted(test.keys())
    
    delivery = dict([])
    inventory = target
    start_date = train_dates[0]
    end_date = train_dates[-1]
    delta = end_date - start_date
    total_fulfillment = 0.0    
    for day in range(delta.days + 1):
        d = start_date+datetime.timedelta(days=day)
        if d in train:
            order = train[d]
        else:
            order = 0
        (percentFulfilled, delivery) = manufacture(cycle, target,  d, inventory, delivery, order)
        total_fulfillment += percentFulfilled
        inv = (inventory-order)
        if d in delivery:
            inv += delivery[d]
        inventory = max(inv, 0)
    percentage_fulfilled = total_fulfillment / sum(train.values())

    print inventory
    vector = produce_vector(train, inventory, delivery, cycle, train_dates[-1])
    print vector

def produce_vector(pastOrders, start_inventory, delivery, cycle_time, start_date):
    inventory = start_inventory - pastOrders[start_date] + delivery[start_date] #if we only have 2 years of data why do we assume to have the orders to leave the warehouse on the first day after our data ends?
    vector = []
    days_with_orders = sorted(pastOrders.keys())
    for cycle_size in range(cycle_time):
        periods = len(days_with_orders) - cycle_size
        numFulfilled = 0.0     
        for day_index in range(periods):
            day = days_with_orders[day_index]
            total_orders = 0.0
            
            for i in range(cycle_size):
                order_date = days_with_orders[day_index+i]
                total_orders += pastOrders[order_date]
                
            if inventory >= total_orders:
                numFulfilled += 1
        vector.append(numFulfilled/periods)
        inventory += delivery[start_date+datetime.timedelta(days=cycle_size+1)]
    return vector
        
   
def manufacture(cycle, target, day, inventory, delivery, order):
    estimate = inventory - order
    for d in range(cycle):
        curr_day = day+datetime.timedelta(days=d)
        if curr_day in delivery:
            estimate += delivery[curr_day]
    if estimate < target:
        delivery[day+datetime.timedelta(days=cycle)] = 30000
    else:
        delivery[day+datetime.timedelta(days=cycle)] = 0

    return (numberFulfilled(inventory, order), delivery)


def numberFulfilled(inventory, order):
    if order==0:
        return order
    elif inventory > order:
        return order
    else:
        return inventory


# pastOrders is a dictionary from item --> date ---> total order for that date
# testDays is the number of days we want to use for test (these will be the last x days in data, not the first)
def split_data(itemNumber, pastOrders, testDays):
    itemOrders = pastOrders[itemNumber]
    train = dict([])
    test = dict([])
    dates = itemOrders.keys()
    dates.sort()
    maxDate = dates[-1]-datetime.timedelta(days=testDays)
    for d in dates:
        if d <= maxDate:
            train[d] = itemOrders[d]
        else:
            test[d] = itemOrders[d]
    return train, test


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
