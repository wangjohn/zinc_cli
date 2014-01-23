Welcome to Zinc
===============

`Zinc <http://zinc.io/>`_ is an API for making e-commerce purchases. This package allows you to easily access the API and make purchases on Amazon through the command line. It also offers wrappers around the Zinc API that can be used easily in python code. 

The module features:
  - Interactive wizard for purchasing Amazon items from the command line
  - Simple order script that reads your order information from a json file and places the order
  - Python module that allows you to write your own scripts on top of the Zinc API

Quick Start
===========

For starting quickly, you can either clone the repo or use the pip python package manager.::

  pip install zinc

Once you've installed the Zinc module, you can start using it like so::

  python -m zinc

This will bring up an interactive wizard interface that you can use the make Amazon purchases. Just grab the URL for any product on Amazon, and following the instructions in the wizard. You'll be able to make a purchase directly in your terminal!

CLI Options
===========

There are other ways of using the Zinc CLI. You can create json files for your shipping address, billing address, and credit card information so you don't have to type them in every time you make an order. You can run `python -m zinc -h` to get help for the commands that you can use.

For example, I might have the file `/home/john/zinc_cli/examples/shipping_address.json` with the following contents::

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

Then I could run the cli with the `-sa` option pointing to this shipping address file::

  python -m zinc -sa /home/john/zinc_cli/examples/shipping_address.json

You can do the same things for billing address and credit card information. The `examples` folder has a number examples that you can try. For example, if you wanted to place an Amazon order for clothing hangers with pre-populated shipping address and credit card information, you could do::

  python -m zinc -p http://www.amazon.com/Honey-Can-Do-HNGZ01523-Light-Weight-Plastic-Hangers/dp/B0037QGRR4 -sa examples/shipping_address.json -c examples/credit_card.json

Simple Order
============

If you don't like going through the process of making orders through the interactive cli, you can also use the Zinc simple order module. This is a python module which allows you to make orders by pre-specifying all of your required fields in a python dictionary or a json file.

You can see an example of the simple order format in `examples/simple_order.json`, reproduced below::

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

Once you've written this down into a json file, you can run::

  python -m zinc -s -f examples/simple_order.json

For making simple orders, you just need to prepopulate all the relevant information like shipping address, billing address, payment method information, etc. The `product_id` field corresponds to the Amazon Standard Identification Number (ASIN), which can be found in the Amazon product url.

Shipping Methods
----------------

For the `shipping_preference` item, you can set different preferences for how you want your items shipped. The available preferences are:

- `cheapest`: Select the cheapest shipping method available
- `second`: Select second day shipping
- `standard`: Select the standard shipping method

Python Usage
============

Instead of using the CLI, you can also import the `zinc` module into one of your python scripts. This allows you to customize and automate your Amazon purchases.::

  from zinc import ZincSimpleOrder

  result = ZincSimpleOrder().process({
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

You can check out an example python script that processes orders from a python file concurrently. The script is in `examples/multi_process.py`. Check out the documentation in the source to see more ways that you can access the API.

Contact
=======

If you would like to learn more about Zinc or place a large number of orders on Amazon in an automated way, please contact <support@zinc.io>. We've got infrastructure set up to help you out!
