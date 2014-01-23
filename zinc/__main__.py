from zinc_wizard import ZincWizard
from zinc_simple_order import ZincSimpleOrder
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Place orders on Amazon without ever leaving the terminal')
    parser.add_argument("-s", "--simple_order", help="Place an order using the simple order format, must use either the '-f' or '-d' option with this.",
            default=False,
            action='store')
    parser.add_argument("-p", "--product_url", help="The url to the Amazon product",
            default=None,
            action='store')
    parser.add_argument("-sa", "--shipping_address", help="The file where you've stored your shipping address information",
            default=None,
            action='store')
    parser.add_argument("-c", "--credit_card", help="The file where you've stored your credit card information",
            default=None,
            action='store')
    parser.add_argument("-ba", "--billing_address", help="The file where you've stored your billing address information",
            default=None,
            action='store')
    parser.add_argument("-g", "--gift", help="Use this option to send the item as a gift",
            default=None,
            action='store_true')
    parser.add_argument("-t", "--client_token", help="Use a client token from Zinc to place your orders using your Amazon account. Contact support@zinc.io to get a client token.",
            default="public",
            action='store')
    parser.add_argument("-cct", "--credit_card_token", help="A token to use to access stored billing information through Zinc's API",
            default=None,
            action='store')
    parser.add_argument("-r", "--retailer", help="Change the retailer you're buying from",
            default="amazon",
            action='store')
    parser.add_argument("-f", "--filename", help="The filename of the simple order. Contents should be in json format.",
            default=None,
            action='store')
    parser.add_argument("-d", "--data", help="Data for the simple order. Must be in json format.",
            default=None,
            action='store')

    args = parser.parse_args()

    if args.simple_order:
        simple_order_main(args)
    else:
        ZincWizard(
                product_url=args.product_url,
                shipping_address=args.shipping_address,
                credit_card=args.credit_card,
                cc_token=args.credit_card_token,
                billing_address=args.billing_address,
                gift=args.gift,
                client_token=args.client_token
                ).start()

def simple_order_main(args):
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
