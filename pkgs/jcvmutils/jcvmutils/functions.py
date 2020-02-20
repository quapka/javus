def is_hex(value):
    try:
        int(value, 16)
        return True
    except ValueError:
        return False
