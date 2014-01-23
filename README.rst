Welcome to Zinc
===============

[Zinc](http://zinc.io/) is an API for making e-commerce purchases. This package allows you to easily access the API and make purchases on Amazon through the command line. 

Quick Start
-----------

For the quick start, just clone the repo and run the `zinc_interactive.py` file. You can either run

.. code-block:: bash
  python zinc_interactive.py


This will bring up an interactive wizard interface that you can use the make Amazon purchases.

CLI Options
-----------

There are other ways of using the Zinc CLI. You can create json files for your shipping address, billing address, and credit card information so you don't have to type them in every time you make an order. You can run `python zinc_interactive.py -h` to get help for the commands that you can use.

For example, I might have the file `/home/john/zinc_cli/examples/shipping_address.json` with the following contents:

.. code-block:: json
  {
    "first_name": "Tim",
    "last_name": "Beaver",
    "address_line1": "77 Massachusetts Avenue",
    "address_line2": "",
    "zip_code": "02139",
    "city": "Cambridge",·
    "state": "MA",
    "country": "US"
  }

Then I could run the cli with the `-s` option pointing to this shipping address file:

.. code-block:: bash
  python zinc_interactive.py -s /home/john/zinc_cli/examples/shipping_address.json

You can do the same things for billing address and credit card information. The `examples` folder has a number examples that you can try. For example, if you wanted to place an Amazon order for clothing hangers with pre-populated shipping address and credit card information, you could do:

.. code-block:: bash
  python zinc_interactive.py -p http://www.amazon.com/Honey-Can-Do-HNGZ01523-Light-Weight-Plastic-Hangers/dp/B0037QGRR4 -s examples/shipping_address.json -c examples/credit_card.json

Simple Order
------------

If you don't like going through the process of making orders through the interactive cli, you can also use the Zinc simple order module. This is a python module which allows you to make orders by pre-specifying all of your required fields in a python dictionary or a json file.

You can see an example of the simple order format in `examples/simple_order.json`, reproduced below:

.. code-block:: json
  {
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
  }

For the simple order module, you just need to prepopulate all the relevant information, like shipping address, billing address, payment method information, etc. The `product_id` field corresponds to the Amazon Standard Identification Number (ASIN), which can be found in the Amazon product url.

The `shipping_preference`.
