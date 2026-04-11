import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bitmath_impl as bm


class TestBitMath(unittest.TestCase):
    def test_basic_helpers(self):
        source = [1, 0, 1]
        copied = bm.copy_bits(source)
        self.assertEqual(bm.zero_bits(4), [0, 0, 0, 0])
        self.assertEqual(copied, source)
        self.assertIsNot(copied, source)
        self.assertEqual(bm.gcd(-12, 8), 4)
        self.assertEqual(bm.gcd(0, 0), 1)
        self.assertEqual(bm.reduce_fraction(0, 9), (0, 1))
        self.assertEqual(bm.reduce_fraction(6, 8), (3, 4))
        self.assertEqual(bm.bits_to_unsigned([1, 0, 1, 1]), 11)
        self.assertEqual(bm.unsigned_to_bits(5, 4), [0, 1, 0, 1])
        self.assertEqual(bm.dec_to_binary_unsigned(5, 4), [0, 1, 0, 1])

    def test_direct_code_and_range_errors(self):
        positive = bm.dec_to_direct(5)
        negative = bm.dec_to_direct(-5)
        self.assertEqual(len(positive), 32)
        self.assertEqual(positive[0], 0)
        self.assertEqual(negative[0], 1)
        self.assertEqual(bm.direct_to_ones(positive), positive)
        self.assertEqual(bm.twos_to_dec(bm.direct_to_twos(negative)), -5)
        with self.assertRaises(ValueError):
            bm.dec_to_direct(2 ** 31)

    def test_twos_complement_helpers(self):
        left = bm.direct_to_twos(bm.dec_to_direct(2))
        right = bm.direct_to_twos(bm.dec_to_direct(3))
        result = bm.add_twos(left, right)
        min_negative = [1] + [0] * 31
        self.assertEqual(bm.twos_to_dec(result), 5)
        self.assertEqual(bm.twos_to_dec(bm.negate_twos(left)), -2)
        self.assertEqual(bm.twos_to_dec(min_negative), -(2 ** 31))
        self.assertEqual(bm.shift_left(left, 0), left)
        self.assertEqual(bm.shift_left(left, 1)[-2:], [0, 0])
        self.assertEqual(bm.magnitude_bits(bm.dec_to_direct(-3))[0], 0)

    def test_mul_and_div(self):
        product = bm.mul_direct(bm.dec_to_direct(-3), bm.dec_to_direct(4))
        zero_product = bm.mul_direct(bm.dec_to_direct(-3), bm.dec_to_direct(0))
        division = bm.div_direct(bm.dec_to_direct(1), bm.dec_to_direct(3))
        negative_division = bm.div_direct(bm.dec_to_direct(-1), bm.dec_to_direct(2))
        self.assertEqual(bm.twos_to_dec(bm.direct_to_twos(product)), -12)
        self.assertEqual(zero_product[0], 0)
        self.assertEqual(division, (0, 0, [0, 1, 0, 1, 0]))
        self.assertEqual(negative_division, (1, 0, [1, 0, 0, 0, 0]))
        self.assertIsNone(bm.div_direct(bm.dec_to_direct(5), bm.dec_to_direct(0)))

    def test_decimal_parsing(self):
        self.assertEqual(bm.parse_decimal('+1,5'), (3, 2))
        self.assertEqual(bm.parse_decimal('.5'), (1, 2))
        self.assertEqual(bm.normalize_decimal_text('-2.5'), ('2.5', -1))
        self.assertEqual(bm.split_decimal_parts('.75'), ('0', '75'))
        with self.assertRaises(ValueError):
            bm.parse_decimal('')
        with self.assertRaises(ValueError):
            bm.split_decimal_parts('1.2.3')
        with self.assertRaises(ValueError):
            bm.split_decimal_parts('ab')

    def test_fraction_helpers(self):
        self.assertEqual(bm.round_division(5, 2), 2)
        self.assertEqual(bm.round_division(7, 2), 4)
        self.assertEqual(bm.compare_fraction_to_power_of_two(3, 2, 0), 1)
        self.assertEqual(bm.compare_fraction_to_power_of_two(1, 2, -1), 0)
        self.assertEqual(bm.compare_fraction_to_power_of_two(1, 2, 0), -1)
        self.assertEqual(bm.floor_log2_fraction(3, 2), 0)
        self.assertEqual(bm.floor_log2_fraction(1, 8), -3)
        self.assertEqual(bm.floor_log2_fraction(1, 3), -2)
        self.assertEqual(bm.floor_log2_fraction(9, 4), 1)
        self.assertEqual(bm.scale_significand(3, 2, 0), (3 << 23, 2))
        self.assertEqual(bm.scale_significand(3, 2, 30), (3, 2 << 7))

    def test_special_ieee_helpers(self):
        inf_bits = bm.build_special_ieee754('inf', 1)
        nan_bits = bm.build_special_ieee754('nan')
        self.assertEqual(inf_bits[0], 1)
        self.assertEqual(bm.bits_to_unsigned(inf_bits[1:9]), 255)
        self.assertEqual(bm.bits_to_unsigned(nan_bits[9:]), 1)
        self.assertEqual(bm.ieee754_inf(-1), inf_bits)
        self.assertEqual(bm.ieee754_nan(), nan_bits)
        self.assertEqual(bm.init_ieee754_bits(0), (bm.zero_bits(), 0, 0))
        bits, sign_bit, abs_num = bm.init_ieee754_bits(-7)
        self.assertEqual((bits[0], sign_bit, abs_num), (1, 1, 7))

    def test_subnormal_and_normal_builders(self):
        zero_sub = bm.build_subnormal_ieee754(1, 1 << 200, 0)
        one_sub = bm.build_subnormal_ieee754(1, 1 << 149, 0)
        rounded_sub = bm.build_subnormal_ieee754(1 << 200, 1, 1)
        self.assertEqual(zero_sub, bm.zero_bits())
        self.assertEqual(bm.bits_to_unsigned(one_sub[1:9]), 0)
        self.assertEqual(bm.bits_to_unsigned(one_sub[9:]), 1)
        self.assertEqual(bm.bits_to_unsigned(rounded_sub[1:9]), 1)
        self.assertEqual(bm.normalize_significand(5, 7, 0), (5, 7, None))
        self.assertEqual(bm.normalize_significand(1 << 24, 126, 0), (1 << 23, 127, None))
        _, _, special = bm.normalize_significand(1 << 24, 127, 1)
        self.assertEqual(bm.ieee754_to_decimal_string(special), '-inf')
        normal = bm.build_normal_ieee754(3, 2, 0, 0)
        overflow = bm.build_normal_ieee754(1 << 128, 1, 0, 127)
        self.assertEqual(bm.ieee754_to_decimal_string(normal, 5), '1.5')
        self.assertEqual(bm.ieee754_to_decimal_string(overflow), 'inf')

    def test_ieee_from_rational_and_decoders(self):
        zero = bm.ieee754_from_rational(0, 1)
        finite = bm.ieee754_from_rational(3, 2)
        subnormal = bm.ieee754_from_rational(1, 1 << 149)
        inf = bm.ieee754_from_rational(1 << 200, 1)
        self.assertEqual(zero, bm.zero_bits())
        self.assertEqual(bm.ieee754_to_decimal_string(finite, 5), '1.5')
        self.assertEqual(bm.bits_to_unsigned(subnormal[1:9]), 0)
        self.assertEqual(bm.ieee754_to_decimal_string(inf), 'inf')
        self.assertIsNone(bm.decode_special_value(0, 0, 1))
        self.assertEqual(bm.decode_special_value(255, 0, -1), ('inf', -1, 0, 1))
        self.assertEqual(bm.decode_special_value(255, 1, 1), ('nan', 1, 0, 1))
        self.assertEqual(bm.decode_finite_value(0, 0), ('zero', 0, 1, 0))
        self.assertEqual(bm.decode_finite_value(0, 5), ('finite', 5, 1 << 23, -126))
        self.assertEqual(bm.decode_finite_value(127, 0), ('finite', 1 << 23, 1 << 23, 0))

    def test_ieee_to_rational_and_decimal_strings(self):
        finite = bm.ieee754_from_decimal('1.5')
        nan_bits = bm.ieee754_nan()
        inf_bits = bm.ieee754_inf(-1)
        self.assertEqual(bm.apply_binary_exponent(3, 4, 2), (12, 4))
        self.assertEqual(bm.apply_binary_exponent(3, 4, -2), (3, 16))
        self.assertEqual(bm.ieee754_to_rational(finite), ('finite', 1, 3, 2))
        self.assertEqual(bm.ieee754_to_rational(nan_bits), ('nan', 1, 0, 1))
        self.assertEqual(bm.ieee754_to_rational(inf_bits), ('inf', -1, 0, 1))
        self.assertEqual(bm.rational_to_decimal_string(0, 1, 5), '0')
        self.assertEqual(bm.rational_to_decimal_string(6, 3, 0), '2')
        self.assertEqual(bm.rational_to_decimal_string(15, 10, 5), '1.5')
        self.assertEqual(bm.rational_to_decimal_string(1, 20000, 3), '0')
        self.assertEqual(bm.ieee754_to_decimal_string(nan_bits), 'NaN')
        self.assertEqual(bm.ieee754_to_decimal_string(inf_bits), '-inf')

    def test_ieee_special_arithmetic(self):
        one = bm.ieee754_from_int(1)
        zero = bm.ieee754_from_int(0)
        inf = bm.ieee754_inf(1)
        neg_inf = bm.ieee754_inf(-1)
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_add(inf, neg_inf)), 'NaN')
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_sub(inf, inf)), 'NaN')
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_add(inf, one)), 'inf')
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_sub(one, inf)), '-inf')
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_mul(inf, zero)), 'NaN')
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_mul(neg_inf, bm.ieee754_from_int(2))), '-inf')
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_div(zero, zero)), 'NaN')
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_div(one, zero)), 'inf')
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_div(one, inf)), '0')
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_div(inf, bm.ieee754_from_int(-2))), '-inf')

    def test_ieee_nan_and_invalid_operation(self):
        nan_bits = bm.ieee754_nan()
        one = bm.ieee754_from_int(1)
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_add(nan_bits, one)), 'NaN')
        with self.assertRaises(ValueError):
            bm.ieee754_binary_operation(one, one, 'bad-op')

    def test_ieee_arithmetic_normal_values(self):
        left = bm.ieee754_from_decimal('1.5')
        right = bm.ieee754_from_decimal('2.25')
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_add(left, right), 5), '3.75')
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_sub(bm.ieee754_from_decimal('5.5'), bm.ieee754_from_int(2)), 5), '3.5')
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_mul(left, bm.ieee754_from_int(2)), 5), '3')
        self.assertEqual(bm.ieee754_to_decimal_string(bm.ieee754_div(bm.ieee754_from_int(7), bm.ieee754_from_int(2)), 5), '3.5')

    def test_excess3_encoding_and_addition(self):
        self.assertEqual(bm.digit_to_excess3(0), [0, 0, 1, 1])
        self.assertEqual(bm.digit_to_excess3(9), [1, 1, 0, 0])
        self.assertEqual(bm.excess3_add(4, 5)[-1], [1, 1, 0, 0])
        self.assertEqual(len(bm.excess3_add(7, 8)), 2)
        self.assertEqual(len(bm.excess3_add(99, 1)), 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
