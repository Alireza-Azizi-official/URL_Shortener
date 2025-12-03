import string

ALPHABET = string.digits + string.ascii_letters


def encode_base62(num: int):
    if num == 0:
        return ALPHABET[0]
    base = len(ALPHABET)
    s = []
    while num:
        num, rem = divmod(num, base)
        s.append(ALPHABET[rem])
    return "".join(reversed(s))


def decode_base62(s: str):
    base = len(ALPHABET)
    num = 0
    for ch in s:
        num = num * base + ALPHABET.index(ch)
    return num
