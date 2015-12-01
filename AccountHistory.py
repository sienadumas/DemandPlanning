# OrderHistory Object
from SkuHistory import SkuHistory
import accounts
import csv
import datetime
import os
import shutil

test_train = True

class AccountHistory:

    def __init__(self, file_name, account_name):
        self.cycle, self.order_size, self.inventory, self.week_order_days = accounts.ACCOUNT[account_name]
        self.past_orders = self.read_csv_data(file_name) # dictionary from item_num to sku object
        self.update_days_of_week()
        if test_train:
            self.generate_train_test()

    def read_csv_data(self, file_name):
        input_file = csv.DictReader(open(file_name))
        data = dict([])

        for row in input_file:
            item_num = int(row["Item #"].replace(",",""))
            raw_date = row["Invoice Date"].split("/")
            date = datetime.date(int(raw_date[2]), int(raw_date[0]), int(raw_date[1]))
            amnt = float(row["Requested Quantity"].replace(",",""))
            if item_num in data.keys():
                data[item_num].update_orders(date, amnt)
            else:
                sku = SkuHistory(item_num, self.cycle, self.order_size, self.inventory, self.week_order_days)
                sku.update_orders(date, amnt)
                data[item_num] = sku
        return data


    def update_days_of_week(self):
        for sku_num in self.past_orders:
            sku = self.past_orders[sku_num]
            sku_dates = sku.orders.keys()
            sku_dates.sort()
            start_date = sku_dates[0]
            end_date = sku_dates[-1]
            delta = end_date - start_date
            for day in range(delta.days+1):
                d = start_date+datetime.timedelta(days=day)
                if (d not in sku.orders) and (d.weekday() in self.week_order_days):
                    sku.orders[d] = 0.0

    # generate test of todays orders
    def generate_train_test(self):
        valid_skus = dict([])
        for item_num in self.past_orders:
            current_sku = self.past_orders[item_num]
            sku_dates = sorted(current_sku.orders.keys())
            start_date_of_orders = sku_dates[0]
            end_date_of_orders = sku_dates[-1]

            (train, test) = current_sku.split_data(1)
            current_sku.orders = train
            current_sku.todays_orders = test

            delta = end_date_of_orders - start_date_of_orders
            if delta.days >= current_sku.cycle:
                valid_skus[item_num] = self.past_orders[item_num]
        self.past_orders = valid_skus

    def write_to_file(self):
        if os.path.exists("results"):
            shutil.rmtree("results")
        os.mkdir("results")
        for item in self.past_orders.keys():
            # dir_name = "results/"+"SKU_" + str(item)
            # os.mkdir(dir_name)

            sku = self.past_orders[item]
            sku.find_threshold(90)
            file_name = "results" + "/" + str(item) + ".txt"
            output = open(file_name, "w")
            output.write('{\n')
            output.write('\tsku_id: ' + str(sku.sku_number) + '\n')
            output.write('\tsku_name: test' + '\n')
            output.write('\tinventory: ' + str(sku.sim_inventory) + '\n')
            total = 0
            for date in sorted(sku.delivery.keys()[len(sku.delivery.keys())-61:]):
                total += sku.delivery[date]
            output.write('\tplanned_production: ' + str(total) + '\n')
            output.write('\t[\n')
            for percent in range(90, 100):
                # sku = self.past_orders[item]
                sku.find_threshold(percent)
                # vector = sku.generate_vector()
                # self.delivery = dict([])
                # file_name = dir_name + "/" + str(item) + "_" + str(percent) + ".csv"
                # output = open(file_name, "w")
                # output.write("Minimum inventory to achieve " + str(percent) + "% fulfillment:\n")
                # output.write(str(sku.threshold) + "\n\n")
                # output.write("Probability vector:\n")
                # output.write(str(vector).replace("[","").replace("]","") + "\n\n")
                # output.write("Delivery:\n")
                # sorted_delivery_dates = sorted(sku.delivery.keys())
                # for date in sorted_delivery_dates:
                #     d = str(date.month) + "/" + str(date.day) + "/" + str(date.year)
                #     output.write(d + "," + str(sku.delivery[date]) + "\n")

                output.write('\t\t{\n')
                output.write('\t\t\tthreshold: ' + str(sku.threshold) + '\n')
                output.write('\t\t\treal_fulfillment: ' + str(sku.fulfilled) + '\n')
                output.write('\t\t\tfulfillment_target: ' + str(percent) + '\n')
                output.write('\t\t\tsurplus: ' + str(sku.todays_surplus) + '\n')
                output.write('\t\t\tsuggested_order: ' + str(sku.delivery[sorted(sku.delivery.keys())[-1]]) + '\n')
                output.write('\t\t}')
                if percent < 99:
                    output.write(',\n')
                else:
                    output.write('\n')
            output.write('\t]\n')
            output.write('}\n')


                

        # goes through each sku
        # for each threshold
        # gets the manufacture orders/shortfall
        # vector
        # writes it to a file

        # for each threshold, shortfall/vector -- 11 files
        # theoretical history
        # actual history
