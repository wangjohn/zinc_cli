from zinc_request_processor import ZincRequestProcessor
import sys
import json

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
            if (x == "y" or x == "n"):
                return True
            else:
                print "You must enter either 'y' or 'n'"
        return validate

class ZincWizard(object):
    PROMPTS = {
        "product_variants": WELCOME_BANNER + "\nPlease please enter a product URL.",
        "product_quantity": "How many would you like to purchase? (Default: 1)",
        "select_product_variants": "This item comes in multiple variants. Please choose an option.",
        "select_shipping_methods": "This item has multiple shipping options. Please choose an option.",
        "security_code": "Please enter the CVV security code on your credit card.",
        "place_order": "Would you like to place this order? (y)/n",
        "gift": "Do you want this to be shipped as a gift? (y)/n",
        "shipping_address": {
            "start_message": "\nNow we'd like to get your shipping information.",
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
            }
        }

    def __init__(self, options = None):
        self.options = (options if options is not None else {})
        self.response_data = {}
        self.security_code = None

    def start(self):
        self.get_product_variants(self.response_data)
        self.get_shipping_methods(self.response_data)
        self.get_store_card(self.response_data)
        self.get_review_order(self.response_data)
        self.get_place_order(self.response_data)

    def prompt(self, prompt, validation=None, max_attempts=3):
        attempts = 0
        while True:
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

    def get_product_variants(self, response_data):
        if "product_url" in self.options:
            product_url = self.options["product_url"]
        else:
            product_url = self.prompt(self.PROMPTS["product_variants"])

        print "\nProcessing request...\n"
        variants_response = ZincRequestProcessor.process("variant_options", {
                    "client_token": self.options["client_token"],
                    "retailer": self.options["retailer"],
                    "product_url": product_url
                    })
        response_data["variant_options_response"] = variants_response
        response_data["products"] = self.select_product_variants(variants_response)

    def get_shipping_methods(self, response_data):
        shipping_address = self.load_file_contents("shipping_address")
        print "\nProcessing request...\n"
        shipping_response = ZincRequestProcessor.process("shipping_methods", {
                    "client_token": self.options["client_token"],
                    "retailer": self.options["retailer"],
                    "products": response_data["products"],
                    "shipping_address": shipping_address
                })

        response_data["shipping_response"] = shipping_response
        response_data["shipping_address"] = shipping_address
        response_data["shipping_method_id"] = self.select_shipping_methods(shipping_response)

    def get_store_card(self, response_data):
        if "cc_token" in self.options and self.options["cc_token"] != None:
            response_data["cc_token"] = self.options["cc_token"]
        else:
            cc_data = self.load_file_contents("credit_card")
            print "\nProcessing request...\n"
            store_card_response = ZincRequestProcessor.process("store_card", {
                        "client_token": self.options["client_token"],
                        "retailer": self.options["retailer"],
                        "billing_address": self.load_file_contents("billing_address"),
                        "number": cc_data["number"],
                        "expiration_month": cc_data["expiration_month"],
                        "expiration_year": cc_data["expiration_year"]
                    })

            response_data["store_card_response"] = store_card_response
            response_data["cc_token"] = store_card_response["cc_token"]

    def get_review_order(self, response_data):
        payment_method = {
                "cc_token": response_data["cc_token"],
                "security_code": self.get_security_code()
                }
        is_gift = self.get_is_gift()
        print "\nProcessing request...\n"
        review_order_response = ZincRequestProcessor.process("review_order", {
                    "client_token": self.options["client_token"],
                    "retailer": self.options["retailer"],
                    "products": response_data["products"],
                    "shipping_address": response_data["shipping_address"],
                    "is_gift": is_gift,
                    "shipping_method_id": response_data["shipping_method_id"],
                    "payment_method": payment_method,
                    "customer_email": "support@zinc.io"
                })

        response_data["review_order_response"] = review_order_response

    def get_place_order(self, response_data):
        self.print_price_components(response_data)
        if self.prompt_boolean(self.PROMPTS["place_order"]):
            print "\nProcessing request...\n"
            place_order_resonse = ZincRequestProcessor.process("place_order", {
                        "client_token": self.options["client_token"],
                        "place_order_key": response_data["review_order_response"]["place_order_key"]
                    })

            response_data["place_order_response"] = place_order_response
            print "HOORAY! You've successfully placed an order. Here are the details:\n"
            print "Amazon Order Id: %s" % place_order_response["merchant_order"]["merchant_order_id"]
            print "Total Price: %s" % place_order_response["price_components"]["total"]
            print place_order_response["shipping_method"]["name"] + ": " + place_order_response["shipping_method"]["description"]

    def print_price_components(self, response_data):
        components = response_data["review_order_response"]["price_components"]
        self.print_indent("Product Subtotal: %s" % self.format_price(components["subtotal"]))
        self.print_indent("Shipping Cost:    %s" % self.format_price(components["shipping"]))
        self.print_indent("Tax:              %s" % self.format_price(components["tax"]))
        if "gift_card" in components:
            self.print_indent("Gift Card:        %s" % self.format_price(components["gift_card"]))
        self.print_indent("Total:            %s" % self.format_price(components["total"]))

    def print_indent(self, value):
        print "    ", value

    def get_is_gift(self):
        if "gift" in self.options:
            return self.options["gift"]
        return self.prompt_boolean(self.PROMPTS["gift"])

    def get_security_code(self):
        if self.security_code != None:
            return self.security_code
        return self.prompt(self.PROMPTS["security_code"])

    def load_file_contents(self, filetype):
        if filetype in self.options and self.options[filetype] != None:
            with open(self.options[filetype], 'rb') as f:
                return json.loads(f.read())
        elif filetype == "shipping_address":
            print self.PROMPTS[filetype]["start_message"]
            return self.get_address(filetype)
        elif filetype == "billing_address":
            if self.prompt_boolean(self.PROMPTS[filetype]["start_message"]):
                return self.response_data["shipping_address"]
            else:
                return self.get_address(filetype)
        elif filetype == "credit_card":
            return self.get_credit_card_information()

    def get_credit_card_information(self):
        print self.PROMPTS["credit_card"]["start_message"]
        response = {}
        response["number"] = self.prompt(self.PROMPTS["credit_card"]["number"])
        response["expiration_month"] = self.prompt(self.PROMPTS["credit_card"]["expiration_month"])
        response["expiration_year"] = self.prompt(self.PROMPTS["credit_card"]["expiration_year"])
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
            self.get_address(filetype)

    def build_prompt(self, base_prompt, description_list):
        prompt = base_prompt + "\n"
        prompt += "\n".join(description_list)
        return prompt

    def select_product_variants(self, variants_response):
        descriptions = []
        product_ids = []
        if (len(variants_response["variant_options"]) > 1):
            for i in xrange(len(variants_response["variant_options"])):
                current_descriptions_list = []
                current_option = variants_response["variant_options"][i]
                for dimension in current_option["dimensions"]:
                    current_descriptions_list.append(dimension["name"] + ": " + dimension["value"])
                if "unit_price" in current_option:
                    current_descriptions_list.append("Price: " + self.format_price(current_option["unit_price"]))
                product_ids.append(current_option["product_id"])
                descriptions.append(str(i) + ") " + ", ".join(current_descriptions_list))

            prompt = self.build_prompt(self.PROMPTS["select_product_variants"], descriptions)

            description_number = self.prompt(prompt, 
                    ValidationHelpers.validate_number(len(descriptions)))
            chosen_product_id = product_ids[int(description_number)]
        else:
            chosen_product_id = variants_response["variant_options"][0]["product_id"]

        quantity = self.get_quantity()
        return [{
                "product_id": chosen_product_id,
                "quantity": quantity
                }]

    def format_price(self, price):
        price = str(price)
        if len(price) > 2:
            return "$" + price[:(-2)] + "." + price[(-2):]
        elif len(price) == 2:
            return "$0." + price
        elif len(price) == 1:
            return "$0.0" + price

    def get_quantity(self):
        quantity = self.prompt(self.PROMPTS["product_quantity"]).strip()
        if quantity == "":
            return 1
        else:
            return quantity

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
                ValidationHelpers.validate_number(len(descriptions)))
        chosen_id = shipping_ids[int(description_number)]
        return chosen_id

if __name__ == '__main__':
    ZincWizard({'retailer': 'amazon',
        'client_token': 'public',
        #'shipping_address': "examples/shipping_address.json",
        #'billing_address': "examples/shipping_address.json",
        #'credit_card': "examples/credit_card.json"
        }).start()
