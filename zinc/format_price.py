def format_price(price):
    price = str(price)
    is_negative = False
    if len(price) > 0 and price[0] == "-":
        is_negative = True
        price = price[1:]

    if len(price) > 2:
        result = "$" + price[:(-2)] + "." + price[(-2):]
    elif len(price) == 2:
        result = "$0." + price
    else:
        result = "$0.0" + price

    if is_negative:
        return "-" + result
    else:
        return result

