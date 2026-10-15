class OrderError(Exception):
    pass


def reserve(items):
    return {"items": list(items)}


def release(reservation):
    reservation["items"].clear()


def charge(customer, amount):
    return {"customer": customer, "amount": amount}


def refund(receipt):
    receipt["amount"] = 0


def ship(order, reservation):
    if not order["address"]:
        raise OrderError("no address")


def place_order(order):
    if not order["items"]:
        raise OrderError("empty order")
    reservation = reserve(order["items"])
    try:
        receipt = charge(order["customer"], order["total"])
    except Exception:
        release(reservation)
        raise
    try:
        ship(order, reservation)
    except Exception:
        refund(receipt)
        release(reservation)
        raise
    return receipt
