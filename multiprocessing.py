from multiprocessing import Pool
from zinc_request_processor import ZincSimpleOrder
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

class ZincConcurrentSimpleOrders(object):
    def __init__(self, num_processes=8):
        self.pool = Pool(processes=num_processes)

    def process_single(self, order_details):
        simple_order = ZincSimpleOrder()
        try:
            response = simple_order.process(order_details)
            return ZincResponse(order_details, response, "successful")
        except:
            error_message = traceback.format_exc()
            return ZincResponse(order_details, error_message, "failed")

    def process(self, orders):
        return self.pool.map(self.process_single, orders)

if __name__ == '__main__':
    filename = "examples/"
    with open(filename, 'rb') as f:
        orders = json.loads(f.read())
    results = ZincConcurrentSimpleOrders(orders).process()

    failed_orders = []
    for result in results:
        if result.failed():
            print "FAILED!"
            failed_orders.append(result.order_details)

    json_to_write = {"failed_orders": failed_orders}
    with open(failed_filename, 'wb') as f:
        f.write(json.dumps(json_to_write))
