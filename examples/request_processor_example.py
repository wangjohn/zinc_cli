###############################################################################
#
# ZincRequestProcessor Example
#
# This is an example of how to use the ZincRequestProcessor class. You can use
# it as a wrapper around the Zinc API. You must specify two things in order to
# process a request: 1) a payload and 2) an API call.
#
# The payloads given in this example will not return correctly because they use
# invalid amazon credentials (in the +retailer_credentials+ field) and also an
# invalid credit card number.
#
###############################################################################

from zinc import ZincRequestProcessor

# PRODUCT VARIANTS
# Get all the possible product variants for this URL.
payload = {
        "client_token": "public",
        "retailer": "amazon",
        "product_url": "http://www.amazon.com/gp/product/0394800761"
        }
product_variants_response = ZincRequestProcessor.process("variant_options", payload)

# Pick the first product variant from the list of results
first_variant = product_variants_response["variant_options"][0]
chosen_product_id = first_variant["product_id"]

# SHIPPING METHODS
# Get the possible ways to ship the product
payload = {
        "client_token": "public",
        "retailer": "amazon",
        "products": [{
            "product_id": chosen_product_id,
            "quantity": 1
            }],
        "shipping_address": {
            "first_name": "Tim",
            "last_name": "Beaver",
            "address_line1": "77 Massachusetts Avenue",
            "address_line2": "",
            "zip_code": "02139",
            "city": "Cambridge", 
            "state": "MA",
            "country": "US"
            },
        "retailer_credentials": {
            "email": "amazonuser@email.com",
            "password": "myAmznPw1"
            }
        }
shipping_methods_response = ZincRequestProcessor.process("shipping_methods", payload)

# Pick the first shipping method from the list of shipping method results
first_method = shipping_methods_response["shipping_methods"][0]
chosen_shipping_method_id = first_method["shipping_method_id"]

# STORE CARD
# Now add a credit card
payload = {
        "client_token": "public",
        "number": "1927376293820990",
        "expiration_month": 1,
        "expiration_year": 2015,
        "billing_address": {
            "first_name": "William", 
            "last_name": "Rogers",
            "address_line1": "84 Massachusetts Ave",
            "address_line2": "",
            "zip_code": "02139",
            "city": "Cambridge", 
            "state": "MA",
            "country": "US"
            }
        }
store_card_response = ZincRequestProcessor.process("store_card", payload)
credit_card_token = store_card_response["cc_token"]

# REVIEW ORDER
# Compile all the information together and review the order
payload = {
        "client_token": "public",
        "retailer": "amazon",
        "products": [{
            "product_id": chosen_product_id,
            "quantity": 1
            }],
        "shipping_address": {
            "first_name": "Tim",
            "last_name": "Beaver",
            "address_line1": "77 Massachusetts Avenue",
            "address_line2": "",
            "zip_code": "02139",
            "city": "Cambridge", 
            "state": "MA",
            "country": "US"
            },
        "is_gift": False,
        "shipping_method_id": chosen_shipping_method_id,
        "payment_method": {
            "security_code": "123",
            "cc_token": credit_card_token
            },
        "customer_email": "timbeaver@gmail.com",
        "retailer_credentials": {
            "email": "amazonuser@email.com",
            "password": "myAmznPw1"
            }
        }
review_order_response = ZincRequestProcessor.process("review_order", payload)
place_order_key = review_order_response["place_order_key"]

# PLACE ORDER
# Now finally place the order
payload = {
        "client_token": "public",
        "place_order_key": place_order_key
        }
place_order_response = ZincRequestProcessor.process("place_order", payload)
print place_order_response
