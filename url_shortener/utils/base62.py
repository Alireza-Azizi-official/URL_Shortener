BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode(num: int):
    if num == 0:
        return BASE62[0]
    s = ""
    while num > 0:
        num, rem = divmod(num, 62)
        s = BASE62[rem] + s
    return s
