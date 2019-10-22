def get_trans_id_from_order_id(order_id):
    """Generate the transaction id for a SystemPay transaction from the order id

    :param order_id:
    :return:
    """
    return str(int(order_id) % 900000).zfill(6)
