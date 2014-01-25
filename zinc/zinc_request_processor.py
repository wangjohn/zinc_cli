import requests
import time
import json

class MaximumRequestRetriesExceeded(Exception):
    pass

class ZincTimeoutError(Exception):
    pass

class ZincError(Exception):
    pass

class ZincAsyncRequest(object):
    def __init__(self, url, request_id, abstract_processor, start_time, retries=2):
        self.url = url
        self.request_id = request_id
        self.abstract_processor = abstract_processor
        self.start_time = start_time
        self.retries = retries

    def finished(self):
        return self.abstract_processor.finished(self.url, self.request_id)

    def get_response(self):
        return self.abstract_processor.wait_for_response(self.url, self.request_id, self.start_time)

class ZincRequestProcessor(object):
    """Processor for Zinc API requests.

    Simple wrapper that instantiates and calls the ZincAbstractProcessor.
    Can be used to process either a synchronous request, using the +process+
    method, or an asynchronous request, using the +process_async+ method.

    The +process+ method will block until a request has returned, and the
    +process_async+ method will return a ZincAsyncRequest object which can
    be used to get the response later.
    """
    @classmethod
    def process(klass, request_type, payload,
            zinc_base_url="https://api.zinc.io/v0",
            polling_interval=1.0,
            retries=2):
        processor = ZincAbstractProcessor()
        try:
            return processor.post_request(payload, request_type)
        except ZincError as e:
            if retries > 0:
                return ZincRequestProcessor.process(request_type, payload,
                        zinc_base_url, polling_interval, retries-1)
            else:
                raise e

    @classmethod
    def process_async(klass, request_type, payload,
            zinc_base_url="https://api.zinc.io/v0"):
        processor = ZincAbstractProcessor()
        return processor.post_request(payload, request_type, async=True)

class ZincAbstractProcessor(object):
    """
    Base class for making calls to the Zinc API.

    The main method for this class, +post_request+, takes in a python dictionary
    and a url_stub. The python dictionary should contain all of the data necessary
    to make a Zinc API call, and the url_stub should be the name of one of the
    API calls (e.g. "variant_options", "shipping_methods", "store_card",
    "review_order", or "place_order").

    Example usage would be the following:

        processor = ZincAbstractProcessor()
        payload = {
            "client_token": "public",
            "retailer": "amazon",
            "product_url": "http://www.amazon.com/gp/product/0394800761"
            }
        result = processor.post_request(payload, "variant_options")

    For more examples using the ZincAbstractProcessor, see the "examples/"
    directory.
    """
    def __init__(self, zinc_base_url="https://api.zinc.io/v0", 
            polling_interval = 1.0,
            request_timeout = 180,
            get_request_timeout = 5.0,
            post_request_timeout = 10.0,
            get_request_retries = 3):
        self.zinc_base_url = zinc_base_url
        self.polling_interval = polling_interval
        self.request_timeout = request_timeout
        self.get_request_timeout = get_request_timeout
        self.post_request_timeout = post_request_timeout
        self.get_request_retries = get_request_retries

    def current_url(self, url_stub = None):
        if url_stub:
            return self.zinc_base_url + "/" + url_stub
        else:
            return self.zinc_base_url

    def post_request(self, payload, url_stub, async=False):
        start_time = time.time()
        result = requests.post(self.current_url(url_stub), data=json.dumps(payload), timeout=self.post_request_timeout)
        request_id = result.json()["request_id"]
        if async:
            return ZincAsyncRequest(self.current_url(url_stub), request_id, self, start_time)
        else:
            return self.wait_for_response(self.current_url(url_stub), request_id, start_time)

    def wait_for_response(self, url, request_id, start_time=None):
        if start_time != None and time.time() - start_time > self.request_timeout:
            raise ZincTimeoutError("The request '%s' timed out after '%s' seconds" %
                    (request_id, time.time() - start_time))
        time.sleep(self.polling_interval)
        potential_result = self.finished(url, request_id)
        if potential_result:
            end_time = time.time()
            return potential_result
        else:
            return self.wait_for_response(url, request_id, start_time)

    def finished(self, url, request_id):
        result = self.make_request(url + "/" + request_id, self.get_request_retries)
        result_json = result.json()
        if result_json["_type"] == "error" and result_json["code"] == "request_processing":
            return False
        elif result_json["_type"] == "error":
            raise ZincError(result_json)
        else:
            return result_json

    def make_request(self, full_url, retries):
        try:
            return requests.get(full_url, timeout=self.get_request_timeout)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if retries > 0:
                return self.make_request(full_url, retries-1)
            else:
                raise MaximumRequestRetriesExceeded("Maximum number of request retries exceeded for connecting to the Zinc API")

