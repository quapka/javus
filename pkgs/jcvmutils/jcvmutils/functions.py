def is_hex(value):
    try:
        int(value, 16)
        return True
    except ValueError:
        return False

def valid_aid(aid):
    # split into pairs/bytes
    try:
        aid_bytes = bytes.fromhex(aid)
    except ValueError:
        return False

    len_aid = len(aid_bytes)

    if len_aid < 5:
        return False

    if len_aid > 16:
        return False
    return True
