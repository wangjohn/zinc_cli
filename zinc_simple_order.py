from zinc_request_processor import ZincSimpleOrder
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Place orders on Amazon using the Zinc Simple Order module. Must specify either "-f" or "-d" to place an order.')
    parser.add_argument("-f", "--filename", help="The filename of the simple order. Contents should be in json format.",
            default=None,
            action='store')
    parser.add_argument("-d", "--data", help="Data for the simple order. Must be in json format.",
            default=None,
            action='store')

    args = parser.parse_args()

    if args.filename != None and args.data != None:
        raise Exception("You must specify either filename '-f' or data '-d', but not both.")
    elif args.filename == None and args.data == None:
        raise Exception("You must specify either filename '-f' or data '-d'.")
    elif args.filename != None:
        print "Placing your order from file: '%s'" % args.filename
        print_order_result(ZincSimpleOrder().process_file(args.filename))
    else:
        print "Placing your order!"
        print_order_result(ZincSimpleOrder().process_json(args.data))

def format_price(self, price):
    price = str(price)
    if len(price) > 2:
        return "$" + price[:(-2)] + "." + price[(-2):]
    elif len(price) == 2:
        return "$0." + price
    elif len(price) == 1:
        return "$0.0" + price

def print_order_result(result):
    print "Merchant Order Id:", format_price(result["merchant_order"]["merchant_order_id"])
    print "Subtotal:", format_price(result["price_components"]["subtotal"])
    if "promotion" in result["price_components"]:
        print "Promotion:", format_price(result["price_components"]["promotion"])
    if "gift_certificate" in result["price_components"]:
        print "Gift Certificate:", format_price(result["price_components"]["gift_certificate"])
    print "Shipping:", format_price(result["price_components"]["shipping"])
    print "Tax:", format_price(result["price_components"]["tax"])
    print "Total:", format_price(result["price_components"]["total"])

if __name__ == '__main__':
    main()

