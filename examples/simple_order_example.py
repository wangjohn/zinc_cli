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
  "city": "Cambridge",·
  "state": "MA",
  "country": "US"
},
"is_gift": false,
"customer_email": "benbitdiddle@gmail.com",
"shipping_preference": "cheapest",
"payment_method": {
  "number": "5555555555554444",
  "security_code": "123",
  "expiration_month": 1,
  "expiration_year": 2015
},
"billing_address": {
  "first_name": "Alyssa",
  "last_name": "Hacker",
  "address_line1": "84 Massachusetts Ave",
  "address_line2": "",
  "zip_code": "02139",
  "city": "Cambridge",·
  "state": "MA",
  "country": "US"
}
})

print result

