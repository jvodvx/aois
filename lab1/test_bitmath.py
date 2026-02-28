import unittest
from bitmath_impl import *


class TestBitMath(unittest.TestCase):


    def test_direct_positive(self):
        bits = dec_to_direct(5)
        self.assertEqual(bits[0], 0)
        self.assertEqual(twos_to_dec(direct_to_twos(bits)), 5)

    def test_direct_negative(self):
        bits = dec_to_direct(-5)
        self.assertEqual(bits[0], 1)
        self.assertEqual(twos_to_dec(direct_to_twos(bits)), -5)

    def test_zero(self):
        bits = dec_to_direct(0)
        self.assertEqual(twos_to_dec(direct_to_twos(bits)), 0)


    def test_add_simple(self):
        A = direct_to_twos(dec_to_direct(2))
        B = direct_to_twos(dec_to_direct(3))
        res = add_twos(A, B)
        self.assertEqual(twos_to_dec(res), 5)

    def test_add_negative(self):
        A = direct_to_twos(dec_to_direct(-2))
        B = direct_to_twos(dec_to_direct(3))
        res = add_twos(A, B)
        self.assertEqual(twos_to_dec(res), 1)

    def test_add_two_negative(self):
        A = direct_to_twos(dec_to_direct(-4))
        B = direct_to_twos(dec_to_direct(-6))
        res = add_twos(A, B)
        self.assertEqual(twos_to_dec(res), -10)


    def test_subtraction(self):
        A = direct_to_twos(dec_to_direct(7))
        B = direct_to_twos(dec_to_direct(5))
        res = add_twos(A, negate_twos(B))
        self.assertEqual(twos_to_dec(res), 2)

    def test_subtraction_negative(self):
        A = direct_to_twos(dec_to_direct(3))
        B = direct_to_twos(dec_to_direct(7))
        res = add_twos(A, negate_twos(B))
        self.assertEqual(twos_to_dec(res), -4)


    def test_mul_simple(self):
        A = dec_to_direct(3)
        B = dec_to_direct(4)
        res = mul_direct(A, B)
        self.assertEqual(twos_to_dec(direct_to_twos(res)), 12)

    def test_mul_negative(self):
        A = dec_to_direct(-3)
        B = dec_to_direct(4)
        res = mul_direct(A, B)
        self.assertEqual(twos_to_dec(direct_to_twos(res)), -12)

    def test_mul_two_negative(self):
        A = dec_to_direct(-2)
        B = dec_to_direct(-5)
        res = mul_direct(A, B)
        self.assertEqual(twos_to_dec(direct_to_twos(res)), 10)


    def test_div_simple(self):
        A = dec_to_direct(10)
        B = dec_to_direct(2)
        sign, q, frac = div_direct(A, B)
        self.assertEqual(sign, 0)
        self.assertEqual(q, 5)

    def test_div_negative(self):
        A = dec_to_direct(-9)
        B = dec_to_direct(3)
        sign, q, frac = div_direct(A, B)
        self.assertEqual(sign, 1)
        self.assertEqual(q, 3)

    def test_div_by_zero(self):
        A = dec_to_direct(5)
        B = dec_to_direct(0)
        self.assertIsNone(div_direct(A, B))


    def test_ieee754_zero(self):
        bits = ieee754_from_int(0)
        self.assertEqual(sum(bits), 0)

    def test_ieee754_positive(self):
        bits = ieee754_from_int(8)
        # 8 = 1.0 * 2^3 → порядок = 127 + 3 = 130
        exp = bits[1:9]
        exp_val = 0
        for b in exp:
            exp_val = exp_val * 2 + b
        self.assertEqual(exp_val, 130)


    def test_excess3_add_simple(self):
        res = excess3_add(4, 5)  # 9
        # 9 в Excess-3 = 1100
        self.assertEqual(res[-1], [1, 1, 0, 0])

    def test_excess3_add_carry(self):
        res = excess3_add(7, 8)  # 15
        self.assertEqual(len(res), 2)


if __name__ == "__main__":
    unittest.main()
