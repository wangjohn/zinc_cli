from zinc_request_processor import ZincAbstractProcessor, ZincTimeoutError, \
    MaximumRequestRetriesExceeded, ZincError
from shipping_method_factory import ShippingMethodFactory
import json

class ZincSimpleOrder(object):
    def __init__(self,
            zinc_base_url="https://api.zinc.io/v0",
            max_tries = 3,
            polling_interval= 1.0,
            request_timeout = 180,
            get_request_timeout = 5.0,
            post_request_timeout = 10.0,
            get_request_retries = 3):
        self.shipping_method_factory = ShippingMethodFactory
        self.max_tries = max_tries
        self.processor = ZincAbstractProcessor(zinc_base_url=zinc_base_url,
                polling_interval=polling_interval,
                request_timeout=request_timeout,
                get_request_timeout=get_request_timeout,
                post_request_timeout=post_request_timeout,
                get_request_retries=get_request_retries)

    def process(self, order_details):
        return self._process_helper(order_details, self.max_tries)

    def process_json(self, json_order_details, multiple=False):
        if multiple:
            return self.process_multiple(json.loads(json_order_details))
        else:
            return self.process(json.loads(json_order_details))

    def process_file(self, filename, multiple=False):
        with open(filename, 'rb') as f:
            return self.process_json(f.read(), multiple)

    def _process_helper(self, order_details, tries):
        if tries > 0:
            try:
                shipping_methods_response = self.processor.post_request(
                        self._shipping_methods_details(order_details), "shipping_methods")
                store_card_response = self.processor.post_request(
                        self._store_card_details(order_details), "store_card")
                review_order_response = self.processor.post_request(
                        self._review_order_details(order_details, shipping_methods_response,
                            store_card_response), "review_order")
            except (ZincTimeoutError, MaximumRequestRetriesExceeded, ZincError):
                return self._process_helper(order_details, tries-1)

            # We don't want to retry on place order requests, in case we accidentally
            # place multiple orders.
            place_order_response = self.processor.post_request(
                    self._place_order_details(order_details, review_order_response),
                    "place_order")
            return place_order_response
        else:
            raise Exception("Maximum tries exceeded: unable to place Zinc order")

    def _shipping_methods_details(self, order_details):
        return {
                "client_token": order_details["client_token"],
                "retailer": order_details["retailer"],
                "shipping_address": order_details["shipping_address"],
                "products": self._products(order_details)
                }

    def _store_card_details(self, order_details):
        return {
                "client_token": order_details["client_token"],
                "billing_address": order_details["billing_address"],
                "number": order_details["payment_method"]["number"],
                "expiration_month": order_details["payment_method"]["expiration_month"],
                "expiration_year": order_details["payment_method"]["expiration_year"]
                }

    def _review_order_details(self, order_details, shipping_methods_response,
            store_card_response):
        return {
                "client_token": order_details["client_token"],
                "retailer": order_details["retailer"],
                "products": self._products(order_details),
                "shipping_address": order_details["shipping_address"],
                "is_gift": order_details["is_gift"],
                "shipping_method_id": self._shipping_method_id(order_details,
                    shipping_methods_response),
                "payment_method": {
                    "security_code": order_details["payment_method"]["security_code"],
                    "cc_token": store_card_response["cc_token"]
                    },
                "customer_email": order_details["customer_email"]
                }

    def _place_order_details(self, order_details, review_order_response):
        return {
                "client_token": order_details["client_token"],
                "place_order_key": review_order_response["place_order_key"]
                }

    def _products(self, order_details):
        return [{
            "product_id": order_details["product_id"],
            "quantity": order_details["quantity"]
            }]


    def _shipping_method_id(self, order_details, shipping_methods_response):
        return self.shipping_method_factory.shipping_method(
                order_details["shipping_preference"], shipping_methods_response)
