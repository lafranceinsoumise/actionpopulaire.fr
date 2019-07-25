def vads_trans_id(order_id):
    return str(int(order_id) % 900000).zfill(6)
