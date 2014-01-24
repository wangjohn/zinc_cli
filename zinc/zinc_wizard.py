from zinc_request_processor import ZincRequestProcessor, ZincError
from format_price import format_price
from getpass import getpass
import sys
import os
import json
import re
from subprocess import call
import urllib
import urllib2

WELCOME_BANNER = """
 ____      ____             __                             
|_  _|    |_  _|           [  |                            
  \ \  /\  / /.---.  .---.  | |  .--.   _ .--..--.  .---.  
   \ \/  \/ // /__\\/ /'`\] | |/ .'`\ \[ `.-. .-. |/ /__\\ 
    \  /\  / | \__.,| \__.  | || \__. | | | | | | || \__., 
     \/  \/   '.__.''.___.'[___]'.__.' [___||__||__]'.__.' 
                                                           
                     _________                             
                    |  _   _  |                            
                    |_/ | | \_|.--.                        
                        | |  / .'`\ \                      
                       _| |_ | \__. |                      
                      |_____| '.__.'                       
                                                           
            ________   _                   _               
           |  __   _| (_)                 | |              
           |_/  / /   __   _ .--.   .---. | |              
              .'.' _ [  | [ `.-. | / /'`\]| |              
            _/ /__/ | | |  | | | | | \__. |_|              
           |________|[___][___||__]'.___.'(_)              

"""


class ValidationHelpers(object):
    @classmethod
    def validate_number(klass, maximum, minimum=0):
        def validate(x):
            if (int(x) <= maximum and int(x) >= minimum):
                return True
            else:
                print "You must enter a number between %s and %s\n" % (minimum, maximum)
        return validate

    @classmethod
    def validate_boolean(klass):
        def validate(x):
            if (x == "y" or x == "n" or x == ""):
                return True
            else:
                print "You must enter either 'y', 'n', or nothing"
        return validate

    @classmethod
    def validate_credit_card(klass):
        def validate(card_number):
            digit_sum = 0
            num_digits = len(card_number)
            oddeven = num_digits & 1
            for count in range(0, num_digits):
                digit = int(card_number[count])
                if not (( count & 1 ) ^ oddeven ):
                    digit = digit * 2
                if digit > 9:
                    digit = digit - 9
                digit_sum += digit
            if ( (digit_sum % 10) == 0 ):
                return True
            else:
                print "Invalid credit card number"
        return validate

class ZincWizard(object):
    PROMPTS = {
        "search_query": "What do you want to buy? (e.g. black cup)",
        "select_product_name": "Here are your results. Please select a product to purchase.",
        "product_variants": "Please please enter a product URL.",
        "product_quantity": "How many would you like to purchase? (Default: 1)",
        "select_product_variants": "This item comes in multiple variants. Please choose an option.",
        "select_shipping_methods": "This item has multiple shipping options. Please choose an option.",
        "security_code": "Please enter the CVV security code on your credit card.",
        "place_order": "Would you like to place this order? (y)/n",
        "gift": "Do you want this to be shipped as a gift? (y)/n",
        "retailer_credentials": {
            "email": "Please enter your Amazon username (usually your email)",
            "password": "Please enter your Amazon password"
            },
        "shipping_address": {
            "start_message": "\nNow we'd like to get your shipping information. Don't worry if you make a mistake, we'll ask you to verify the correctness of your address so you can retype it if you'd like.\n",
            "end_message": "\nYou've finished entering your shipping address!"
            },
        "address": {
            "first_name": "Please input your first name:",
            "last_name": "Please input your last name:",
            "address_line1": "Please input the first line of your shipping address:",
            "address_line2": "Please input the second line of your shipping address: (optional)",
            "city": "Please input your city:",
            "state": "Please input your state (e.g. CA, MA, etc.):",
            "zip_code": "Please input your zip code:",
            "country": "Please input your country (e.g. US):",
            "confirmation_message": "Is this your correct shipping address? (y)/n"
            },
        "billing_address" : {
            "start_message": "\nIs your billing address the same as your shipping address? (y)/n",
            "end_message": "\nYou've finished entering you billing address!"
            },
        "credit_card": {
            "start_message": "\nNow we'd like to get your credit card information.",
            "number": "Please input your credit card number",
            "expiration_month": "Please input your credit card expiration month (e.g. 03)",
            "expiration_year": "Please input your credit card expiration year (e.g. 2017)",
            "security_code": "Please input the CVV security code from your credit card",
            "end_message": "\nYou've finished entering your credit card information!"
            },
        "write_to_zincrc": "Would you like to write the information you just entered to a configuration file (.zincrc) so you can make orders more easily in the future? We'll only include your shipping address and a hashed credit card token, so no confidential information will be written to your hard drive. (y)/n"
        }

    def __init__(self,
            retailer = "amazon",
            client_token = "public",
            filename = None,
            gift = None,
            ):
        self.retailer = retailer
        self.client_token = client_token
        self.stored_data = self.get_stored_data(filename)
        self.gift = gift

        self.response_data = {}
        self.product_url = None
        self.security_code = None
        self.async_responses = {}
        self.shipping_address = None

    def get_stored_data(self, filename):
        default_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.zincrc")
        if filename != None and os.path.isfile(filename):
            with open(filename, 'rb') as f:
                return json.loads(f.read())
        elif os.path.isfile(default_filename):
            with open(default_filename, 'rb') as f:
                return json.loads(f.read())
        return {}

    def retrieve_data(self, key):
        if key in self.stored_data:
            return self.stored_data[key]
        elif key == "shipping_address":
            print self.PROMPTS[key]["start_message"]
            return self.get_address(key)
        elif key == "billing_address":
            if self.prompt_boolean(self.PROMPTS[key]["start_message"]):
                return self.shipping_address
            else:
                return self.get_address(key)
        elif key == "credit_card":
            return self.get_credit_card_information()

    def start(self):
        print WELCOME_BANNER
        try:
            self.start_interactive_session()
        except ZincError as e:
            self.print_indent("\nUnfortunately there seemed to be an error\n")
            self.print_indent(str(e))
            self.print_indent("\nRestarting...\n")
            self.start_interactive_session()

    def start_interactive_session(self):
        self.get_product_name(self.response_data)
        self.get_product_variants(self.response_data)
        self.get_retailer_credentials(self.response_data)
        self.get_shipping_methods(self.response_data)
        self.get_store_card(self.response_data)
        self.get_review_order(self.response_data)
        self.get_place_order(self.response_data)

    def prompt(self, prompt, validation=None, max_attempts=3, password=False):
        attempts = 0
        while True:
            if password:
                raw = getpass(prompt + "\n")
            else:
                raw = raw_input(prompt + "\n")
            if (validation == None) or (validation != None and validation(raw)):
                return raw
            else:
                attempts += 1
                if attempts >= max_attempts:
                    print "You've reached the maximum number of attempts. Exiting!"
                    sys.exit()

    def prompt_boolean(self, prompt):
        result = self.prompt(prompt, ValidationHelpers.validate_boolean()).strip()
        if (result == "y" or result == ""):
            return True
        return False

    def get_product_name(self, response_data):
        search_query = self.prompt(self.PROMPTS["search_query"])
        print "\nProcessing request...\n"
        product_name_response = ZincRequestProcessor.process("search_products", {
                "client_token": self.client_token,
                "retailer": self.retailer,
                "search_query": search_query
            })

        response_data["product_name_response"] = product_name_response
        self.product_url = self.select_product_name(product_name_response)

    def get_product_variants(self, response_data):
        print "\nProcessing request...\n"
        async_response = ZincRequestProcessor.process_async("variant_options", {
                    "client_token": self.client_token,
                    "retailer": self.retailer,
                    "product_url": self.product_url
                    })
        asin = self.get_asin(self.product_url)
        product_info = None
        if asin != None:
            print call(["curl", "http://ihmage.com/" + asin + "?size=25"])
            product_info = AmazonDataFinder.get_amazon_data(asin)
        variants_response = async_response.get_response()
        response_data["variant_options_response"] = variants_response
        response_data["products"] = self.select_product_variants(variants_response, product_info)

    def get_retailer_credentials(self, response_data):
        print "\nProcessing request...\n"
        email = self.prompt(self.PROMPTS["retailer_credentials"]["email"])
        password = self.prompt(self.PROMPTS["retailer_credentials"]["password"], password=True)
        response_data["retailer_credentials"] = {
                "email": email,
                "password": password
                }

    def get_shipping_methods(self, response_data):
        self.shipping_address = self.retrieve_data("shipping_address")
        print "\nProcessing request...\n"
        shipping_response = ZincRequestProcessor.process_async("shipping_methods", {
                    "client_token": self.client_token,
                    "retailer": self.retailer,
                    "products": response_data["products"],
                    "shipping_address": self.shipping_address,
                    "retailer_credentials": response_data["retailer_credentials"]
                })

        self.async_responses["shipping_response"] = shipping_response

    def get_store_card(self, response_data):
        cc_token = self.retrieve_data("cc_token")
        if cc_token == None:
            cc_data = self.retrieve_data("credit_card")
            self.billing_address = self.retrieve_data("billing_address")
            print "\nProcessing request...\n"
            store_card_response = ZincRequestProcessor.process("store_card", {
                        "client_token": self.client_token,
                        "retailer": self.retailer,
                        "billing_address": self.billing_address,
                        "number": cc_data["number"],
                        "expiration_month": cc_data["expiration_month"],
                        "expiration_year": cc_data["expiration_year"]
                    })

            response_data["store_card_response"] = store_card_response
            self.stored_data["cc_token"] = store_card_response["cc_token"]

    def get_review_order(self, response_data):
        shipping_method_id = self.select_shipping_methods(
                self.async_responses["shipping_response"].get_response())
        payment_method = {
                "prefer_use_gift_balance": True,
                "cc_token": self.retrieve_data("cc_token"),
                "security_code": self.get_security_code()
                }
        is_gift = self.get_is_gift()
        print "\nProcessing request...\n"
        review_order_response = ZincRequestProcessor.process("review_order", {
                    "client_token": self.client_token,
                    "retailer": self.retailer,
                    "products": response_data["products"],
                    "shipping_address": self.shipping_address,
                    "is_gift": is_gift,
                    "shipping_method_id": shipping_method_id,
                    "payment_method": payment_method,
                    "customer_email": "support@zinc.io",
                    "retailer_credentials": response_data["retailer_credentials"]
                })

        response_data["review_order_response"] = review_order_response

    def get_place_order(self, response_data):
        self.write_to_zincrc()
        self.print_price_components(response_data)
        if self.prompt_boolean(self.PROMPTS["place_order"]):
            print "\nProcessing request...\n"
            place_order_response = ZincRequestProcessor.process("place_order", {
                        "client_token": self.client_token,
                        "place_order_key": response_data["review_order_response"]["place_order_key"]
                    })

            response_data["place_order_response"] = place_order_response
            print "HOORAY! You've successfully placed an order. Here are the details:\n"
            print "Amazon Order Id: %s" % place_order_response["merchant_order"]["merchant_order_id"]
            print "Total Price: %s" % format_price(place_order_response["price_components"]["total"])
            print place_order_response["shipping_method"]["name"] + ": " + place_order_response["shipping_method"]["description"]

    def print_price_components(self, response_data):
        components = response_data["review_order_response"]["price_components"]
        self.print_indent("Product Subtotal: %s" % format_price(components["subtotal"]))
        self.print_indent("Shipping Cost:    %s" % format_price(components["shipping"]))
        self.print_indent("Tax:              %s" % format_price(components["tax"]))
        if "gift_certificate" in components:
            self.print_indent("Gift Certificate: %s" % format_price(components["gift_certificate"]))
        if "promotion" in components:
            self.print_indent("Promotion:        %s" % format_price(components["promotion"]))
        self.print_indent("Total:            %s" % format_price(components["total"]))

    def write_to_zincrc(self):
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.zincrc")
        if not os.path.isfile(filename) and self.prompt_boolean(self.PROMPTS["write_to_zincrc"]):
            data = {
                "shipping_address": self.shipping_address,
                "cc_token": self.retrieve_data("cc_token")
                }
            with open(filename, 'w+') as f:
                f.write(json.dumps(data))

    def get_asin(self, product_url):
        match = re.search("/([a-zA-Z0-9]{10})(?:[/?]|$)", product_url)
        if match:
            return match.group(1)

    def print_indent(self, value):
        print "    ", value

    def get_is_gift(self):
        if self.gift != None:
            return self.gift
        return self.prompt_boolean(self.PROMPTS["gift"])

    def get_security_code(self):
        if self.security_code != None:
            return self.security_code
        return self.prompt(self.PROMPTS["security_code"])

    def get_credit_card_information(self):
        print self.PROMPTS["credit_card"]["start_message"]
        response = {}
        response["number"] = self.prompt(self.PROMPTS["credit_card"]["number"],
                ValidationHelpers.validate_credit_card())
        response["expiration_month"] = self.prompt(self.PROMPTS["credit_card"]["expiration_month"],
                ValidationHelpers.validate_number(12, 1))
        response["expiration_year"] = self.prompt(self.PROMPTS["credit_card"]["expiration_year"],
                ValidationHelpers.validate_number(2100, 2010))
        self.security_code = self.prompt(self.PROMPTS["credit_card"]["security_code"])
        print self.PROMPTS["credit_card"]["end_message"]
        return response

    def get_address(self, filetype):
        address = {}
        for label in ["first_name", "last_name", "address_line1", "address_line2",
                "city", "state", "zip_code", "country"]:
            address[label] = self.prompt(self.PROMPTS["address"][label])

        print "\nYou typed the following:\n"
        self.print_indent("    %s %s" % (address["first_name"], address["last_name"]))
        self.print_indent("    %s" % (address["address_line1"]))
        self.print_indent("    %s" % (address["address_line2"]))
        self.print_indent("    %s, %s %s" % (address["city"], address["state"], address["zip_code"]))
        self.print_indent("    %s" % (address["country"]))
        print ""

        if self.prompt_boolean(self.PROMPTS["address"]["confirmation_message"]):
            print self.PROMPTS[filetype]["end_message"]
            return address
        else:
            return self.get_address(filetype)

    def build_prompt(self, base_prompt, description_list):
        prompt = base_prompt + "\n"
        prompt += "\n".join(description_list)
        return prompt

    def get_quantity(self):
        quantity = self.prompt(self.PROMPTS["product_quantity"]).strip()
        if quantity == "":
            return 1
        else:
            return quantity

    def select_product_name(self, response):
        descriptions = []
        collector = []
        for i in xrange(len(response["results"])):
            current = response["results"][i]
            descriptions.append(str(i) + ") " + current["title"])
            asin = self.get_asin(current["product_url"])
            collector.append(current["product_url"])

        prompt = self.build_prompt(self.PROMPTS["select_product_name"], descriptions)
        collected_number = self.prompt(prompt,
                ValidationHelpers.validate_number(len(descriptions)-1))
        return collector[int(collected_number)]

    def select_product_variants(self, variants_response, product_info):
        descriptions = []
        descriptions.append("\nDescription: " + product_info)
        product_ids = []
        if (len(variants_response["variant_options"]) > 1):
            for i in xrange(len(variants_response["variant_options"])):
                current_descriptions_list = []
                current_option = variants_response["variant_options"][i]
                for dimension in current_option["dimensions"]:
                    current_descriptions_list.append(dimension["name"] + ": " + dimension["value"])
                if "unit_price" in current_option:
                    current_descriptions_list.append("Price: " + format_price(current_option["unit_price"]))
                product_ids.append(current_option["product_id"])
                descriptions.append(str(i) + ") " + ", ".join(current_descriptions_list))

            prompt = self.build_prompt(self.PROMPTS["select_product_variants"], descriptions)

            description_number = self.prompt(prompt, 
                    ValidationHelpers.validate_number(len(descriptions)-1))
            chosen_product_id = product_ids[int(description_number)]
        else:
            chosen_product_id = variants_response["variant_options"][0]["product_id"]

        quantity = self.get_quantity()
        return [{
                "product_id": chosen_product_id,
                "quantity": quantity
                }]

    def select_shipping_methods(self, shipping_response):
        descriptions = []
        shipping_ids = []
        for i in xrange(len(shipping_response["shipping_methods"])):
            current_method = shipping_response["shipping_methods"][i]
            descriptions.append(str(i) + ") " + current_method["name"] + \
                    ": " + current_method["description"])
            shipping_ids.append(current_method["shipping_method_id"])

        prompt = self.build_prompt(self.PROMPTS["select_shipping_methods"], descriptions)
        description_number = self.prompt(prompt,
                ValidationHelpers.validate_number(len(descriptions)-1))
        chosen_id = shipping_ids[int(description_number)]
        return chosen_id

class AmazonDataFinder(object):
    @classmethod
    def get_amazon_data(klass, asin):
        url = 'http://bulkbuyingtools.com/index.php'
        values = {'name' : 'Michael Foord',
            's' : 'cb3dd4783d787a78a2c9a4e18b86a426',
            'asin_list' : asin}

        # first request.. make the session key associated with the asin
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        try:
            response = urllib2.urlopen(req, timeout=2)
            the_page = response.read()
            loaded_page = re.search('This ASIN/ISBN number is invalid', \
                the_page, flags=re.DOTALL|re.IGNORECASE)
            if loaded_page is not None: # the ASIN was invalid
                raise RuntimeError('loaded_page is None')
        except:
            return False

        url = 'http://bulkbuyingtools.com/results.php?s=cb3dd4783d787a78a2c9a4e18b86a426'
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        the_page = response.read()

        try:
            ret_price = 0
            ret_description = ''
            price = re.search('<th>Image</th>.*?<th nowrap>Price:</th>\s*<td nowrap><b>\$(.*?)</b>', \
                    the_page, flags=re.DOTALL|re.IGNORECASE)
            if price:
                ret_price = price.group(1)
                description = re.search('<th>Image</th>.*?<li>([^<]*?)(<a.*?</a>)?</li>\s*</ul>', \
                    the_page, flags=re.DOTALL|re.IGNORECASE)
            if description:
                ret_description = description.group(1)

            return ret_description
        except Exception, err:
            return False

if __name__ == '__main__':
    ZincWizard().start()
