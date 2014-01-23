import requests
import time
import json

class MaximumRequestRetriesExceeded(Exception):
    pass

class ZincTimeoutError(Exception):
    pass

class ZincError(Exception):
    pass

class ZincRequestProcessor(object):
    """Processor for Zinc API requests.

    Simple wrapper that instantiates and calls the ZincAbstractProcessor.
    """
    @classmethod
    def process(klass, request_type, payload,
            zinc_base_url="https://api.zinc.io/v0",
            polling_interval=1.0):
        processor = ZincAbstractProcessor()
        return processor.post_request(payload, request_type)

class ZincAbstractProcessor(object):
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

    def post_request(self, payload, url_stub):
        start_time = time.time()
        result = requests.post(self.current_url(url_stub), data=json.dumps(payload), timeout=self.post_request_timeout)
        request_id = result.json()["request_id"]
        return self.wait_for_response(self.current_url(url_stub), request_id, start_time)

    def wait_for_response(self, url, request_id, start_time):
        if time.time() - start_time > self.request_timeout:
            raise ZincTimeoutError("The request '%s' timed out after '%s' seconds" %
                    (request_id, time.time() - start_time))
        time.sleep(self.polling_interval)
        result = self.make_request(url + "/" + request_id, self.get_request_retries)
        result_json = result.json()
        if result_json["_type"] == "error" and result_json["code"] == "request_processing":
            return self.wait_for_response(url, request_id, start_time)
        elif result_json["_type"] == "error":
            raise ZincError(json.dumps(result_json))
        else:
            end_time = time.time()
            return result_json

    def make_request(self, full_url, retries):
        try:
            return requests.get(full_url, timeout=self.get_request_timeout)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if retries > 0:
                return self.make_request(full_url, retries-1)
            else:
                raise MaximumRequestRetriesExceeded("Maximum number of request retries exceeded for connecting to the Zinc API")

