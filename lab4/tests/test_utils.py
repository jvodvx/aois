from utils import (
    get_char_value,
    calculate_v,
    hash_function
)


def test_get_char_value():
    assert get_char_value("A") == 0
    assert get_char_value("B") == 1
    assert get_char_value("Z") == 25


def test_calculate_v():

    # B=1, E=4
    # 1*26 + 4 = 30

    assert calculate_v("Belgium") == 30

    # C=2, H=7
    # 2*26 + 7 = 59

    assert calculate_v("China") == 59


def test_hash_function():

    assert hash_function(30) == 10
    assert hash_function(59) == 19
    assert hash_function(43) == 3