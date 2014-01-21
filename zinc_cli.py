#!/usr/bin/python
from zinc_wizard import ZincWizard
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Place orders on Amazon without ever leaving the terminal')
    parser.add_argument("-p", "--product_url", help="The url to the Amazon product",
            default=None,
            action='store')
    parser.add_argument("-sh", "--shipping_address", help="The file where you've stored your shipping address information",
            default=None,
            action='store')
    parser.add_argument("-cc", "--credit_card", help="The file where you've stored your credit card information",
            default=None,
            action='store')
    parser.add_argument("-t", "--credit_card_token", help="A token to use to access stored billing information through Zinc's API",
            default=None,
            action='store')
    parser.add_argument("-ba", "--billing_address", help="The file where you've stored your billing address information",
            default=None,
            action='store')
    parser.add_argument("-g", "--gift", help="Use this option to send the item as a gift",
            default=None,
            action='store_true')
    parser.add_argument("-ct", "--client_token", help="Use a client token from Zinc to place your orders using your Amazon account. Contact support@zinc.io to get a client token.",
            default="public",
            action='store')
    parser.add_argument("-r", "--retailer", help="Change the retailer you're buying from",
            default="amazon",
            action='store')

    args = parser.parse_args()

    ZincWizard(
            product_url=args.product_url,
            shipping_address=args.shipping_address,
            credit_card=args.credit_card,
            cc_token=args.credit_card_token,
            billing_address=args.billing_address,
            gift=args.gift,
            client_token=args.client_token
            ).start()

if __name__ == '__main__':
    main()
