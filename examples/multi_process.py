from zinc import ZincSimpleOrder
from multiprocessing import Pool
import json
import traceback

class ZincResponse(object):
    def __init__(self, request, response, status):
        self.request = request
        self.response = response
        self.status = status

    def failed(self):
        return self.status == "failed"

    def successful(self):
        return self.status == "successful"

def process_single(order_details):
    simple_order = ZincSimpleOrder()
    try:
        response = simple_order.process(order_details)
        return ZincResponse(order_details, response, "successful")
    except:
        error_message = traceback.format_exc()
        return ZincResponse(order_details, error_message, "failed")

class ZincConcurrentSimpleOrders(object):
    def __init__(self, num_processes=8):
        self.pool = Pool(processes=num_processes)

    def process(self, orders):
        return self.pool.map(process_single, orders)

if __name__ == '__main__':
    filename = "multiple_orders.json"
    failed_filename = "multiple_orders_failed.json"
    with open(filename, 'rb') as f:
        orders = json.loads(f.read())["orders"]
    print "Number of orders:", len(orders)
    results = ZincConcurrentSimpleOrders().process(orders)

    failed_orders = []
    for result in results:
        if result.failed():
            failed_orders.append(result.request)

    print "Number of failed orders:", len(failed_orders)
    json_to_write = {"orders": failed_orders}
    with open(failed_filename, 'wb') as f:
        f.write(json.dumps(json_to_write))
