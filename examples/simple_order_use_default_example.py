###############################################################################
#
# ZincSimpleOrder Example
#
# This is an example of how to use the ZincSimpleOrder class.
#
# Note that the data used in this example will not return correct results
# because they use invalid credit card number.
#
###############################################################################

from zinc import ZincSimpleOrder

simple_order = ZincSimpleOrder()
result = simple_order.process({
    "client_token": "public",
    "retailer": "amazon",
    "product_id": "B007JR5304",
    "quantity": 1,
    "shipping_address": {
      "first_name": "Ben",
      "last_name": "Bitdiddle",
      "address_line1": "77 Massachusetts Avenue",
      "address_line2": "",
      "zip_code": "02139",
      "city": "Cambridge",
      "state": "MA",
      "country": "US"
    },
    "is_gift": false,
    "customer_email": "benbitdiddle@gmail.com",
    "shipping_preference": "cheapest",
    "use_default_payment_method": True
})

print result

