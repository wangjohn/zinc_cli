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
    def validateNumber(klass, maximum, minimum=0):
        def validate(x):
            if (int(x) <= maximum and int(x) >= minimum):
                return True
            else:
                print "You must enter a number between %s and %s\n" % (minimum, maximum)
        return validate

    @classmethod
    def validateBoolean(klass):
        pass

class ZincWizard(object):
    PROMPTS = {
        "product_variants": WELCOME_BANNER + "\nPlease please enter a product URL.",
        "product_quantity": "How many would you like to purchase?",
        "select_product_variants": "This item comes in multiple variants. Please choose an option.",
        "select_shipping_methods": "This item has multiple shipping options. Please choose one."
            }

    def __init__(self, options = None):
        self.options = (options if options is not None else {})

    def start(self):
        response_data = {}
        self.get_product_variants(response_data)
        self.get_shipping_methods(response_data)
        self.get_store_card(response_data)
        self.get_review_order(response_data)
        self.get_place_order(response_data)

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

    def get_product_variants(self, response_data):
        if "product_url" in self.options:
            product_url = self.options["product_url"]
        else:
            product_url = self.prompt(self.PROMPTS["product_variants"])

        variants_response = ZincRequestProcessor.process("variant_options", {
                    "client_token": self.options["client_token"],
                    "retailer": self.options["retailer"],
                    "product_url": product_url
                    })
        response_data["variant_options_response"] = variants_response
        response_data["products"] = self.select_product_variants(variants_response)

    def get_shipping_methods(self, response_data):
        shipping_address = self.load_file_contents("shipping_address")
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
        cc_data = self.load_file_contents("credit_card")
        store_card_response = ZincRequestProcessor.process("store_card", {
                    "client_token": self.options["client_token"],
                    "retailer": self.options["retailer"],
                    "billing_address": self.load_file_contents("billing_address"),
                    "number": cc_data["number"],
                    "expiration_month": cc_data["expiration_month"],
                    "expiration_year": cc_data["expiration_year"]
                })

        response_data["store_card_response"] = store_card_response

    def get_review_order(self, response_data):
        payment_method = {
                "cc_token": response_data["store_card_response"]["cc_token"],
                "security_code": self.get_security_code()
                }
        review_order_response = ZincRequestProcessor.process("review_order", {
                    "client_token": self.options["client_token"],
                    "retailer": self.options["retailer"],
                    "products": response_data["products"],
                    "shipping_address": response_data["shipping_address"],
                    "is_gift": self.options["gift"],
                    "shipping_method_id": response_data["shipping_method_id"],
                    "payment_method": payment_method,
                    "customer_email": self.options["email"]
                })

        response_data["review_order_response"] = review_order_response

    def get_place_order(self, response_data):
        self.prompt(self.PROMPT["place_order"])
        place_order_resonse = ZincRequestProcessor.process("place_order", {
                    "client_token": self.options["client_token"],
                    "place_order_key": response_data["review_order_response"]["place_order_key"]
                })

        response_data["place_order_response"] = place_order_response

    def get_security_code(self):
        # FIXME: do it
        return "123"

    def load_file_contents(self, filetype):
        if filetype in self.options:
            with open(self.options[filetype], 'rb') as f:
                return json.loads(f.read())

    def build_prompt(self, base_prompt, description_list):
        prompt = base_prompt + "\n"
        prompt += "\n".join(description_list)
        return prompt

    def select_product_variants(self, variants_response):
        descriptions = []
        product_ids = []
        for i in xrange(len(variants_response["variant_options"])):
            current_descriptions_list = []
            current_option = variants_response["variant_options"][i]
            for dimension in current_option["dimensions"]:
                current_descriptions_list.append(dimension["name"] + ": " + dimension["value"])
            product_ids.append(current_option["product_id"])
            descriptions.append(str(i) + ") " + ", ".join(current_descriptions_list))

        prompt = self.build_prompt(self.PROMPTS["select_product_variants"], descriptions)

        description_number = self.prompt(prompt, 
                ValidationHelpers.validateNumber(len(descriptions)))
        chosen_product_id = product_ids[int(description_number)]

        quantity = self.prompt(self.PROMPTS["product_quantity"])
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
                ValidationHelpers.validateNumber(len(descriptions)))
        chosen_id = shipping_ids[int(description_number)]
        print "Chosen shipping method id: %s" % chosen_id
        return chosen_id

if __name__ == '__main__':
    ZincWizard({'retailer': 'amazon',
        'client_token': 'public',
        'shipping_address': "examples/shipping_address.json"
        }).start()
