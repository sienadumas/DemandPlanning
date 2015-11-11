# OrderHistory Object
from SkuHistory import SkuHistory
import accounts
import csv
import datetime

test_train = True

class AccountHistory:

    def __init__(self, file_name, account_name):
        (cycle, order_size, inventory) = accounts.ACCOUNT[account_name]
        self.past_orders = self.read_csv_data(file_name) # dictionary from item_num to sku object
        if test_train:
            self.today = self.generate_train_test()
        else:
            self.today = None # call from db

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
                sku = SkuHistory(item_num)
                sku.update_orders(date, amnt)
                data[item_num] = sku
        return data

    # generate test of todays orders
    def generate_train_test(self):
        today = dict([])
        for item_num in self.past_orders:
            current_sku = self.past_orders[item_num]
            (train, test) = current_sku.split_data(1)
            current_sku.orders = train
            current_sku.todays_orders = test
        return today

    def write_to_file(self):
        print('write to file')
        # for item in self.past_orders.keys():
        #     #create directory
        #     for percent in range(90, 101):
        #         sku = self.past_orders[item]
        #         sku.find_threshold(percent)
        #         sku.generate_vector()

        sku = self.past_orders[866]
        sku.find_threshold(98)
        sku.generate_vector()



                # print percent
                # print sku.threshold
                # print everything

        # goes through each sku
        # for each threshold
        # gets the manufacture orders/shortfall
        # vector
        # writes it to a file

        # for each threshold, shortfall/vector -- 11 files
        # theoretical history
        # actual history
