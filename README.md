Welcome to Zinc
===============

[Zinc](http://zinc.io/) is an API for making e-commerce purchases. This package allows you to easily access the API and make purchases on Amazon through the command line. 

## Quick Start

For the quick start, just clone the repo and run the `zinc_interactive.py` file. You can either run

```
python zinc_interactive.py
```

Or you can turn the file into a script and run it.

```
chmod +x zinc_interactive.py
./zinc_interactive.py
```

This will bring up an interactive wizard interface that you can use the make Amazon purchases.

## CLI Options

There are other ways of using the Zinc CLI. You can create json files for your shipping address, billing address, and credit card information so you don't have to type them in every time you make an order. You can run `python zinc_interactive.py -h` to get help for the commands that you can use.

For example, I might have the file `/home/john/zinc_cli/examples/shipping_address.json` with the following contents:

```
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
```

Then I could run the cli with the `-s` option pointing to this shipping address file:

```
python zinc_interactive.py -s /home/john/zinc_cli/examples/shipping_address.json
```

You can do the same things for billing address and credit card information. The `examples` folder has a number examples that you can try. For example, if you wanted to place an Amazon order for clothing hangers with pre-populated shipping address and credit card information, you could do:

```
python zinc_interactive.py -p http://www.amazon.com/Honey-Can-Do-HNGZ01523-Light-Weight-Plastic-Hangers/dp/B0037QGRR4 -s examples/shipping_address.json -c examples/credit_card.json
```

## Simple Order

If you don't like going through the process of making orders through the interactive cli, you can also use the Zinc simple order module. This is a python module which allows you to make orders by pre-specifying all of your required fields in a python dictionary or a json file.

