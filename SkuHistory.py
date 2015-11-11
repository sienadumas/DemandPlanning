import datetime

class SkuHistory:
    def __init__(self, sku_number, cycle=60, order_size=1000, inventory=5000):
        self.sku_number = sku_number
        self.orders = dict([]) #date -> number
        self.threshold = 5000
        self.cycle = cycle
        self.order_size = order_size
        self.inventory = inventory # live in future, simulated now
        self.delivery = dict([])
        self.todays_orders = None
        self.fulfilled = 0

    def update_orders(self, date, count):
        if date in self.orders:
            self.orders[date] = self.orders[date]+count
        else:
            self.orders[date] = count

    def find_threshold(self, percent):
        while self.fulfilled*100 < percent:
            print(self.sku_number, self.fulfilled, self.threshold, percent)
            # delivery completely updated
            self.threshold += 1000
            self.inventory = self.threshold
            self.fulfilled = self.calculate_percent_filfilled()
        print(self.sku_number, self.fulfilled, self.threshold, percent)


    def calculate_percent_filfilled(self):
        dates = sorted(self.orders.keys())
        start_date = dates[0]
        end_date = dates[-1]
        delta = end_date - start_date
        total_fulfillment = 0.0
        for day in range(delta.days + 1):
            d = start_date+datetime.timedelta(days=day)
            if d in self.orders:
                order = self.orders[d]
            else:
                order = 0
            fulfilled = self.estimated_shortfall(d, order)
            total_fulfillment += fulfilled
            inv = (self.inventory-order)
            if d in self.delivery:
                inv += self.delivery[d]
            self.inventory = max(inv, 0)
        percentage_fulfilled = total_fulfillment / sum(self.orders.values())
        return percentage_fulfilled


    # calculates the shortfall for today
    # appends it onto the manufacturing dictionary
    def estimated_shortfall(self, day, order):        
        estimate = self.inventory - order
        for d in range(self.cycle):
            curr_day = day+datetime.timedelta(days=d)
            if curr_day in self.delivery:
                estimate += self.delivery[curr_day]
        if estimate < self.threshold:
            self.delivery[day+datetime.timedelta(days=self.cycle)] = self.order_size
        else:
            self.delivery[day+datetime.timedelta(days=self.cycle)] = 0

        return self.number_fulfilled(order)

    def number_fulfilled(self, order):
        if order == 0:
            return order
        elif self.inventory > order:
            return order
        else:
            return self.inventory

    def generate_vector(self):
        days_with_orders = sorted(self.orders.keys())
        # start_date = self.todays_orders.keys()[0]
        start_date = days_with_orders[-1]
        print(start_date)

        curr_inventory = self.inventory - self.orders[start_date] + self.delivery[start_date] #if we only have 2 years of data why do we assume to have the orders to leave the warehouse on the first day after our data ends?
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
            curr_inventory += self.delivery[start_date+datetime.timedelta(days=cycle_size+1)]
        print(vector)
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

