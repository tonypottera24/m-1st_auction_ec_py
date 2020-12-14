

def tx_print(tx_receipt, s):
    if tx_receipt['status'] == 0:
        print("{} failed, used {:,} gas".format(s,
                                                tx_receipt['gasUsed']), flush=True)
        print(tx_receipt)
        exit(1)
    else:
        print("{} success, used {:,} gas".format(s,
                                                 tx_receipt['gasUsed']), flush=True)
