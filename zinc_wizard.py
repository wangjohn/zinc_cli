from zinc_request_processor import ZincRequestProcessor
import sys
import json

class ValidationHelpers(object):
    @classmethod
    def validateNumber(klass, maximum, minimum=0):
        def validate(x):
            if (int(x) <= maximum and int(x) >= minimum):
                return True
            else:
                print "You must enter a number between %s and %s\n" % (minimum, maximum)
        return validate

class ZincWizard(object):
    PROMPTS = {
        "product_variants": "Welcome to Zinc!\nPlease please enter a product URL.",
        "select_product_variants": "This item comes in multiple variants. Please choose an option."
        "select_shipping_methods": "This item has multiple shipping options. Please choose one."
            }

    def __init__(self, options = None):
        self.options = (options if options is not None else {})

    def start(self):
        response_data = {}
        response_data["products"] = self.get_product_variants()
        response_data["shipping_method_id"] = self.get_shipping_methods(response_data)
        response_data["store_card_response"] = self.get_store_card(response_data)

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

    def get_product_variants(self):
        if "product_url" in self.options:
            product_url = self.options["product_url"]
        else:
            product_url = self.prompt(self.PROMPTS["product_variants"])

        variants_response = ZincRequestProcessor.process("variant_options", {
                    "client_token": self.options["client_token"],
                    "retailer": self.options["retailer"],
                    "product_url": product_url
                    })
        return self.select_product_variants(variants_response)

    def get_shipping_methods(self, response_data):
        shipping_response = ZincRequestProcessor.process("shipping_methods", {
                    "client_token": self.options["client_token"],
                    "retailer": self.options["retailer"],
                    "products": response_data["products"],
                    "shipping_address": self.load_file_contents("shipping_address")
                })

        return self.select_shipping_methods(shipping_response)

    def get_store_card(self, response_data):
        cc_data = self.load_file_contents("credit_card")
        store_card_response = ZincRequestProcessor.process("store_card", {
                    "client_token": self.options["client_token"],
                    "retailer": self.options["retailer"],
                    "billing_address": self.load_file_contents("billing_address")
                    "number": cc_data["number"],
                    "expiration_month": cc_data["expiration_month"],
                    "expiration_year": cc_data["expiration_year"]
                })

        return store_card_response

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

        quantity = self.prompt("How many would you like to purchase?")
        return [{
                "product_id": chosen_product_id,
                "quantity": quantity
                }]

    def select_shipping_methods(self, shipping_response):
        descriptions = []
        shipping_ids = []
        for i in xrange(len(shipping_response["shipping_methods"])):
            current_method = shipping_response["shipping_methods"][i]
            descriptions.append(current_method["name"] + ": " + current_method["description"])
            shipping_ids.append(current_method["shipping_method_id"])

        prompt = self.build_prompt(self.PROMPTS["select_shipping_methods"], descriptions)
        description_number = self.prompt(prompt,
                ValidationHelpers.validateNumber(len(descriptions)))
        chosen_id = shipping_ids[int(description_number)]

        return chosen_id

if __name__ == '__main__':
    ZincWizard({'retailer': 'amazon',
        'client_token': 'public',
        'shipping_address': "examples/shipping_address.json"
        }).start()
