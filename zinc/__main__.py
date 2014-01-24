from zinc_wizard import ZincWizard
from zinc_simple_order import ZincSimpleOrder
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Place orders on Amazon without ever leaving the terminal')
    parser.add_argument("-s", "--simple_order", help="Place an order using the simple order format, must use either the '-f' or '-d' option with this.",
            default=False,
            action='store')
    parser.add_argument("-g", "--gift", help="Use this option to send the item as a gift",
            default=None,
            action='store_true')
    parser.add_argument("-t", "--client_token", help="Use a client token from Zinc to place your orders using your Amazon account. Contact support@zinc.io to get a client token.",
            default="public",
            action='store')
    parser.add_argument("-r", "--retailer", help="Change the retailer you're buying from",
            default="amazon",
            action='store')
    parser.add_argument("-f", "--filename", help="The file which contains metadata such as shipping address, credit card information, and billing address. Contents should be in json format.",
            default="~/.zincrc",
            action='store')

    args = parser.parse_args()

    if args.simple_order:
        simple_order_main(args)
    else:
        ZincWizard(
                filename=args.filename,
                retailer=args.retailer,
                gift=args.gift,
                client_token=args.client_token
                ).start()

def simple_order_main(args):
    if args.filename == None:
        raise Exception("You must specify a filename '-f' to read data from when using the '-s' simple order option.")
    print_order_result(ZincSimpleOrder().process_file(args.filename))

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
