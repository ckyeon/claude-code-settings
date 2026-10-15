from formatting import format_price


def apply_discount(price, rate):
    return price * (1 - rate)


def price_label(price, rate):
    return format_price(apply_discount(price, rate))
