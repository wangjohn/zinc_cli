zinc_purchase -t simple_order -d '
{
  "client_token": "public",
  "retailer": "amazon",
  "product_id": "B007JR5304",
  "quantity": 1,
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
  "is_gift": false,
  "customer_email": "timbeaver@gmail.com",
  "shipping_preference": "cheapest",
  "payment_method": {
    "number": "1927376293820990",
    "security_code": "123",
    "expiration_month": 1,
    "expiration_year": 2015
  },
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
}'
