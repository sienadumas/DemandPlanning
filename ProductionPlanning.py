# The function to return csv for production planning
# Parameter is account

import sys
import accounts
from AccountHistory import AccountHistory

def main():
    name = sys.argv[1] #plum
    version = sys.argv[2] #simulation

    past_orders = AccountHistory(name)
    past_orders.write_to_db_file()



main()
