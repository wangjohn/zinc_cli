Welcome to Zinc
===============

[Zinc](http://zinc.io/) is an API for making e-commerce purchases. This package allows you to easily access the API and make purchases on Amazon through the command line. 

Quick Start
===========

For the quick start, just clone the repo and run the `zinc_cli.py` file. You can either run

```
python zinc_cli.py
```

Or you can turn the file into a script and run it.

```
chmod +x zinc_cli.py
./zinc_cli.py
```

This will bring up an interactive wizard interface that you can use the make Amazon purchases.

CLI Options
===========

There are other ways of using the Zinc CLI. You can create json files for your shipping address, billing address, and credit card information so you don't have to type them in every time you make an order.

For example, I might have the file `/home/john/zinc_cli/my_example_shipping_address.json` with the following contents:

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
python zinc_cli.py -s /home/john/zinc_cli/my_example_shipping_address.json
```

You can do the same things for billing address and credit card information. The `examples` folder has a number examples that you can try.


