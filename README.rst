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

  sudo pip install zinc

Once you've installed the Zinc module, you can start using it like so::

  python -m zinc

This will bring up an interactive wizard interface that you can use the make Amazon purchases. Follow the instructions in the wizard, and you'll be able to make a purchase directly from your terminal!

CLI Options
===========

There are other ways of using the Zinc CLI. You can create a json file which will store your shipping and billing information. You can run `python -m zinc -h` to get help for the commands that you can use. For example, I might have the file `~/.zincrc` with the following contents::

  {
    "shipping_address": {
      "first_name": "Tim",
      "last_name": "Beaver",
      "address_line1": "77 Massachusetts Avenue",
      "address_line2": "",
      "zip_code": "02139",
      "city": "Cambridge",·
      "state": "MA",
      "country": "US"
    },
    "billing_address": {
      "first_name": "Alyssa",
      "last_name": "Hacker",
      "address_line1": "77 Massachusetts Avenue",
      "address_line2": "",
      "zip_code": "02139",
      "city": "Cambridge",·
      "state": "MA",
      "country": "US"
    }
  }

Then I could run the cli with the `-f` option pointing to this shipping address file so that I wouldn't have to enter my shipping address again in the interactive wizard::

  python -m zinc -f ~/.zincrc

You can include credit card information if you'd like (we have an example in the `examples/sample_information.json` for reference), but we highly discourage you from including it. **It's a BAD idea to leave your credit card information on your hard drive in plaintext.**

The `examples` folder has an example file that has fake prepopulated information that you can try. You won't be able to complete a full purchase with it, though, because it's a fake credit card number. To run the wizard with the fake information, you can do::

  python -m zinc -f examples/sample_information.json

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

Once you've written this down into a json file, you can specify the `-s` option (for simple order) and you can run::

  python -m zinc -s -f examples/simple_order.json

To make simple orders, you just need to prepopulate all the relevant information like shipping address, billing address, payment method information, etc. The `product_id` field corresponds to the `Amazon Standard Identification Number (ASIN) <http://en.wikipedia.org/wiki/Amazon_Standard_Identification_Number>`_, which can be found in the Amazon product url. You will aslo need to set the `shipping_preference` field, explained in the next section.

Shipping Methods
----------------

For the `shipping_preference` item, you can set different preferences for how you want your items shipped. The available preferences are:

- `cheapest`: Select the cheapest shipping method available
- `second`: Select second day shipping
- `standard`: Select the standard shipping method

Python Usage
============

Instead of using the CLI, you can also import the `zinc` module into one of your python scripts. This allows you to customize and automate your Amazon purchases. You can use the `ZincSimpleOrder` class to easily access the Zinc API. You can check out the `examples/simple_order_example.py` script to see how to use it (reproduced below)::

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

You can check out an example python script that processes orders from a python file concurrently. The script is in `examples/multi_process.py`.

Advanced Python Usage
---------------------

If you'd like to get more control over your API, you can use the `ZincRequestProcessor` class to make requests. The `process` method for the `ZincRequestProcessor` class allows you to place any call to the Zinc API and wait for the response. For example, you could do something like the following::

  from zinc import ZincRequestProcessor
  payload = {
      "client_token": "public",
      "retailer": "amazon",
      "product_url": "http://www.amazon.com/gp/product/0394800761"
  }
  result = ZincRequestProcessor.process("variant_options", payload)
  print result

The `process` method returns a python dictionary with the Zinc API's response to your request. Running the previous script would print out the following::

  {
    'product_url': 'http://www.amazon.com/gp/product/0394800761',
    '_created_at': '2014-01-24T21:59:12.755Z',
    '_type': 'variant_options_response',
    'variant_options': [{
        '_type': 'variant_option',
        '_id': '52e2e230ef2840020000020a',
        'product_id': '0394800761',
        'unit_price': '1149',
        'dimensions': []
      }], 
    'retailer': 'amazon'
  }

Check the `Zinc API documentation <http://zinc.io/docs/api.html>`_ to see all of the possible API calls. An example that uses the `ZincRequestProcessor` class to place an entire order is given in `examples/request_processor_example.py`.

Contact
=======

If you would like to learn more about Zinc or place a large number of orders on Amazon in an automated way, please contact <support@zinc.io>. We've got infrastructure set up to help you out!
