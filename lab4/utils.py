from constants import ALPHABET, TABLE_SIZE


def get_char_value(char):
    return ALPHABET.index(char.upper())


def calculate_v(key):

    key = key.upper()

    first = get_char_value(key[0])

    if len(key) > 1:
        second = get_char_value(key[1])
    else:
        second = 0

    return first * 26 + second


def hash_function(v):
    return v % TABLE_SIZE