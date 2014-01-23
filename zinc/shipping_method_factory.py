class ShippingMethodFactory(object):
    @classmethod
    def shipping_method(klass, shipping_preference, shipping_methods_response):
        if hasattr(klass, shipping_preference):
            return getattr(klass, shipping_preference)(shipping_methods_response)
        else:
            raise TypeError("The shipping preference '%s' is not supported." % shipping_preference)

    @classmethod
    def cheapest(klass, shipping_methods_response):
        minimum = (None, None)
        for method in shipping_methods_response["shipping_methods"]:
            if minimum[0] == None or method["price"] < minimum[0]:
                minimum = (method["price"], method["shipping_method_id"])

        if minimum[0] == None:
            return shipping_methods_response["shipping_methods"][0]["shipping_method_id"]
        else:
            return minimum[1]

    @classmethod
    def second(klass, shipping_methods_response):
        possible_methods = ['second','std-n-us','std-us', 'Std Cont US Street Addr', 'Std US Dom Plus', 'second-non48', 'std-n-us-non48', 'std-us-non48']

        for shipping_id in possible_methods:
            for method in shipping_methods_response["shipping_methods"]:
                if method["shipping_method_id"] == shipping_id:
                    return shipping_id
        raise Exception("The response doesn't have any of the shipping methods you requested")

    @classmethod
    def standard(klass, shipping_methods_response):
        possible_methods = ['std-n-us','std-us', 'Std Cont US Street Addr', 'Std US Dom Plus', 'std-n-us-non48', 'std-us-non48']

        for shipping_id in possible_methods:
            for method in shipping_methods_response["shipping_methods"]:
                if method["shipping_method_id"] == shipping_id:
                    return shipping_id
        raise Exception("The response doesn't have any of the shipping methods you requested")
