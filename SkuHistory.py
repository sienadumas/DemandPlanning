import datetime
import math

class SkuHistory:
    def __init__(self, sku_number, cycle=60, order_size=1000, inventory=5000, week_order_days=[0,1,3,4,5,6]):
        self.sku_number = sku_number
        self.orders = dict([]) #date -> number
        self.threshold = 5000
        self.cycle = cycle
        self.order_size = order_size
        self.sim_inventory = inventory # live in future, simulated now
        self.week_order_days = week_order_days
        self.delivery = dict([])
        self.todays_orders = None
        #self.todays_surplus = 0
        self.fulfilled = 0
        self.test_inventories = dict([])
        self.surplus = dict([])

    # Either increments the orders for the date passed or sets the orders for that date equal to count
    def update_orders(self, date, count):
        if date in self.orders:
            self.orders[date] = self.orders[date]+count
        else:
            self.orders[date] = count

    # Given a percent, finds the minimum inventory that needs to be maintained at all times in order to fulfill that
    # percent of orders. Sets the initial threshold to 5000 and increments by units of 1000 to find the threshold. 
    def find_threshold(self, percent):
        while self.fulfilled*100 < percent:
            self.threshold += 1000
            self.sim_inventory = 75000 # TODO: Omega
            self.fulfilled = self.calculate_percent_fulfilled()
        self.inventory = self.sim_inventory # TODO: realtime

    # Calculates the percentage of orders that are fulfilled (on a unit basis) with the current global threshold and 
    # returns that percentage
    def calculate_percent_fulfilled(self):
        self.delivery = dict([])
        dates = sorted(self.orders.keys())
        start_date = dates[0]
        end_date = dates[-1]
        delta = end_date - start_date
        total_fulfillment = 0.0
        for day in range(delta.days + 1):
            d = start_date+datetime.timedelta(days=day)
            if d.weekday() in self.week_order_days:
                order = self.orders[d] #d will always be in self.orders
                self.update_deliveries(d, order)
                fulfilled = self.number_fulfilled(order)
                total_fulfillment += fulfilled
                inv = (self.sim_inventory-order)
                if d in self.delivery:
                    inv += self.delivery[d]
                self.sim_inventory = max(inv, 0)
        percentage_fulfilled = total_fulfillment / sum(self.orders.values())
        return percentage_fulfilled


    # calculates the shortfall for today
    # appends it onto the manufacturing dictionary
    def update_deliveries(self, day, order):
        estimate = self.sim_inventory - order
        for d in range(self.cycle):
            curr_day = day+datetime.timedelta(days=d)
            if curr_day in self.delivery:
                estimate += self.delivery[curr_day]

        #finds the date that delivery should arrive in (example: if it's a sunday increments until it reaches monday)
        delivery_date = day+datetime.timedelta(days=self.cycle)
        while delivery_date.weekday() not in self.week_order_days:
            delivery_date += datetime.timedelta(days=1)

        if estimate < self.threshold:
            todays_surplus = (self.threshold - estimate) * (-1)
            delivery_amnt = math.ceil((self.threshold - estimate) / self.order_size) * self.order_size
        else:
            todays_surplus = 0
            delivery_amnt = 0

        if delivery_date in self.delivery:
            self.delivery[delivery_date] = self.delivery[delivery_date] + delivery_amnt
        else:
            self.delivery[delivery_date] = delivery_amnt
        self.test_inventories[day] = self.sim_inventory

        self.surplus[day] = (delivery_date, todays_surplus, delivery_amnt)

    # Returns how many units of the passed variable order can be fulfilled given our current inventory 
    def number_fulfilled(self, order):
        if order == 0:
            return order
        elif self.sim_inventory > order:
            return order
        else:
            return self.sim_inventory

    # Generates the probability vector of length cycle_time. Each index represents how many cycle_times we could
    # fulfill where cycle_time for that index is equal to the index+1
    def generate_vector(self):
        days_with_orders = sorted(self.orders.keys())
        start_date, ordered = self.todays_orders.items()[0]
        if start_date in self.delivery:
            delivered = self.delivery[start_date]
        else:
            delivered = 0.0

        curr_inventory = self.sim_inventory - ordered + delivered #if we only have 2 years of data why do we assume to have the orders to leave the warehouse on the first day after our data ends?
        vector = []
        for cycle_size in range(self.cycle):
            periods = len(days_with_orders) - cycle_size
            num_fulfilled = 0.0     
            for day_index in range(periods):
                day = days_with_orders[day_index]
                total_orders = 0.0
                
                for i in range(cycle_size):
                    order_date = days_with_orders[day_index+i]
                    total_orders += self.orders[order_date]
                    
                if curr_inventory >= total_orders:
                    num_fulfilled += 1
            vector.append(num_fulfilled/periods)

            delivery_date = start_date+datetime.timedelta(days=cycle_size+1)
            if delivery_date in self.delivery:
                curr_inventory += self.delivery[delivery_date]
        return vector


    # self.orders is a dictionary from date ---> total order for that date
    # testDays is the number of days we want to use for test (these will be the last x days in data, not the first)
    def split_data(self, testDays):
        train = dict([])
        test = dict([])
        dates = self.orders.keys()
        dates.sort()
        maxDate = dates[-1]-datetime.timedelta(days=testDays)
        for d in dates:
            if d <= maxDate:
                train[d] = self.orders[d]
            else:
                test[d] = self.orders[d]
        return train, test

