BITS = 32
EXP_BITS = 8
MANTISSA_BITS = 23
BIAS = 127
DIV_PRECISION = 5


def zero_bits(size: int = BITS):
    return [0] * size


def copy_bits(a):
    return a[:]


def gcd(a: int, b: int) -> int:
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a or 1


def reduce_fraction(num: int, den: int):
    if num == 0:
        return 0, 1
    div = gcd(num, den)
    return num // div, den // div


def bits_to_unsigned(bits) -> int:
    value = 0
    for bit in bits:
        value = value * 2 + bit
    return value


def unsigned_to_bits(value: int, size: int) -> list:
    bits = [0] * size
    for index in range(size - 1, -1, -1):
        bits[index] = value % 2
        value //= 2
    return bits


def dec_to_binary_unsigned(n: int, size: int = BITS - 1) -> list:
    return unsigned_to_bits(n, size)


def dec_to_direct(n: int) -> list:
    if abs(n) >= 2 ** (BITS - 1):
        raise ValueError("Число не помещается в 32-битный прямой код.")

    bits = zero_bits()
    if n < 0:
        bits[0] = 1
        n = -n

    magnitude = dec_to_binary_unsigned(n, BITS - 1)
    bits[1:] = magnitude
    return bits


def direct_to_ones(bits: list) -> list:
    result = copy_bits(bits)
    if result[0] == 1:
        for index in range(1, BITS):
            result[index] = 1 - result[index]
    return result


def ones_to_twos(bits: list) -> list:
    result = copy_bits(bits)
    carry = 1
    for index in range(BITS - 1, -1, -1):
        total = result[index] + carry
        result[index] = total % 2
        carry = total // 2
    return result


def direct_to_twos(bits: list) -> list:
    if bits[0] == 0:
        return copy_bits(bits)
    return ones_to_twos(direct_to_ones(bits))


def add_twos(a: list, b: list) -> list:
    result = zero_bits()
    carry = 0
    for index in range(BITS - 1, -1, -1):
        total = a[index] + b[index] + carry
        result[index] = total % 2
        carry = total // 2
    return result


def negate_twos(bits: list) -> list:
    inverted = [1 - bit for bit in bits]
    return ones_to_twos(inverted)


def twos_to_dec(bits: list) -> int:
    if bits[0] == 1 and all(bit == 0 for bit in bits[1:]):
        return -(2 ** (BITS - 1))

    if bits[0] == 0:
        return bits_to_unsigned(bits[1:])

    magnitude = negate_twos(bits)
    return -bits_to_unsigned(magnitude[1:])


def shift_left(bits: list, amount: int) -> list:
    if amount <= 0:
        return copy_bits(bits)

    result = zero_bits()
    for index in range(amount, BITS):
        result[index - amount] = bits[index]
    return result


def magnitude_bits(bits: list) -> list:
    result = zero_bits()
    result[1:] = bits[1:]
    return result


def mul_direct(a: list, b: list) -> list:
    left = magnitude_bits(a)
    right = magnitude_bits(b)
    result = zero_bits()

    for offset, index in enumerate(range(BITS - 1, 0, -1)):
        if right[index] == 1:
            result = add_twos(result, shift_left(left, offset))

    if any(result[1:]):
        result[0] = a[0] ^ b[0]
    return result


def div_direct(a: list, b: list):
    dividend = bits_to_unsigned(a[1:])
    divisor = bits_to_unsigned(b[1:])
    if divisor == 0:
        return None

    sign = a[0] ^ b[0]
    integer_part = dividend // divisor
    remainder = dividend % divisor
    fraction_bits = []

    for _ in range(DIV_PRECISION):
        remainder *= 2
        if remainder >= divisor:
            fraction_bits.append(1)
            remainder -= divisor
        else:
            fraction_bits.append(0)

    return sign, integer_part, fraction_bits


def parse_decimal(value: str):
    text, sign = normalize_decimal_text(value)
    whole, fraction = split_decimal_parts(text)
    digits = whole + fraction
    numerator = int(digits) if digits else 0
    return reduce_fraction(numerator * sign, 10 ** len(fraction))


def normalize_decimal_text(value: str):
    text = value.strip().replace(',', '.')
    if not text:
        raise ValueError("Пустая строка.")
    sign = 1
    if text[0] in '+-':
        sign = -1 if text[0] == '-' else 1
        text = text[1:]
    return text, sign


def split_decimal_parts(text: str):
    if text.count('.') > 1:
        raise ValueError("Некорректный формат числа.")
    whole, _, fraction = text.partition('.')
    if whole == '':
        whole = '0'
    if not whole.isdigit() or (fraction and not fraction.isdigit()):
        raise ValueError("Некорректный формат числа.")
    return whole, fraction


def round_division(num: int, den: int) -> int:
    quotient, remainder = divmod(num, den)
    doubled = remainder * 2
    if doubled > den or (doubled == den and quotient % 2 == 1):
        quotient += 1
    return quotient


def compare_fraction_to_power_of_two(num: int, den: int, exponent: int) -> int:
    if exponent >= 0:
        left = num
        right = den << exponent
    else:
        left = num << (-exponent)
        right = den

    if left > right:
        return 1
    if left < right:
        return -1
    return 0


def floor_log2_fraction(num: int, den: int) -> int:
    exponent = num.bit_length() - den.bit_length()
    while compare_fraction_to_power_of_two(num, den, exponent) < 0:
        exponent -= 1
    while compare_fraction_to_power_of_two(num, den, exponent + 1) >= 0:
        exponent += 1
    return exponent


def build_special_ieee754(kind: str, sign_bit: int = 0) -> list:
    bits = zero_bits()
    bits[0] = sign_bit
    bits[1:9] = [1] * EXP_BITS
    if kind == 'nan':
        bits[-1] = 1
    return bits


def ieee754_inf(sign: int) -> list:
    return build_special_ieee754('inf', 1 if sign < 0 else 0)


def ieee754_nan() -> list:
    return build_special_ieee754('nan')


def init_ieee754_bits(num: int):
    bits = zero_bits()
    if num == 0:
        return bits, 0, 0
    sign_bit = 1 if num < 0 else 0
    bits[0] = sign_bit
    return bits, sign_bit, abs(num)


def build_subnormal_ieee754(abs_num: int, den: int, sign_bit: int) -> list:
    bits = zero_bits()
    bits[0] = sign_bit
    mantissa = round_division(abs_num << 149, den)
    if mantissa == 0:
        return zero_bits()
    if mantissa >= (1 << MANTISSA_BITS):
        bits[1:9] = unsigned_to_bits(1, EXP_BITS)
        return bits
    bits[9:] = unsigned_to_bits(mantissa, MANTISSA_BITS)
    return bits


def scale_significand(abs_num: int, den: int, exponent: int):
    if exponent <= MANTISSA_BITS:
        return abs_num << (MANTISSA_BITS - exponent), den
    return abs_num, den << (exponent - MANTISSA_BITS)


def normalize_significand(significand: int, exponent: int, sign_bit: int):
    limit = 1 << (MANTISSA_BITS + 1)
    if significand != limit:
        return significand, exponent, None
    significand //= 2
    exponent += 1
    if exponent > 127:
        return significand, exponent, ieee754_inf(-1 if sign_bit else 1)
    return significand, exponent, None


def build_normal_ieee754(abs_num: int, den: int, sign_bit: int, exponent: int) -> list:
    bits = zero_bits()
    bits[0] = sign_bit
    scaled_num, scaled_den = scale_significand(abs_num, den, exponent)
    significand = round_division(scaled_num, scaled_den)
    significand, exponent, special = normalize_significand(significand, exponent, sign_bit)
    if special is not None:
        return special
    bits[1:9] = unsigned_to_bits(exponent + BIAS, EXP_BITS)
    bits[9:] = unsigned_to_bits(significand - (1 << MANTISSA_BITS), MANTISSA_BITS)
    return bits


def ieee754_from_rational(num: int, den: int) -> list:
    num, den = reduce_fraction(num, den)
    bits, sign_bit, abs_num = init_ieee754_bits(num)
    if abs_num == 0:
        return bits

    exponent = floor_log2_fraction(abs_num, den)
    if exponent > 127:
        return ieee754_inf(-1 if sign_bit else 1)
    if exponent < -126:
        return build_subnormal_ieee754(abs_num, den, sign_bit)
    return build_normal_ieee754(abs_num, den, sign_bit, exponent)


def ieee754_from_int(n: int) -> list:
    return ieee754_from_rational(n, 1)


def ieee754_from_decimal(value: str) -> list:
    numerator, denominator = parse_decimal(value)
    return ieee754_from_rational(numerator, denominator)


def decode_special_value(exponent_field: int, mantissa_field: int, sign: int):
    if exponent_field != 255:
        return None
    if mantissa_field == 0:
        return 'inf', sign, 0, 1
    return 'nan', sign, 0, 1


def decode_finite_value(exponent_field: int, mantissa_field: int):
    if exponent_field == 0 and mantissa_field == 0:
        return 'zero', 0, 1, 0
    if exponent_field == 0:
        return 'finite', mantissa_field, 1 << MANTISSA_BITS, -126
    numerator = (1 << MANTISSA_BITS) + mantissa_field
    return 'finite', numerator, 1 << MANTISSA_BITS, exponent_field - BIAS


def apply_binary_exponent(numerator: int, denominator: int, exponent: int):
    if exponent >= 0:
        return numerator << exponent, denominator
    return numerator, denominator << (-exponent)


def ieee754_to_rational(bits: list):
    sign = -1 if bits[0] == 1 else 1
    exponent_field = bits_to_unsigned(bits[1:9])
    mantissa_field = bits_to_unsigned(bits[9:])
    special = decode_special_value(exponent_field, mantissa_field, sign)
    if special is not None:
        return special

    kind, numerator, denominator, exponent = decode_finite_value(exponent_field, mantissa_field)
    if kind == 'zero':
        return 'zero', sign, 0, 1
    numerator, denominator = apply_binary_exponent(numerator, denominator, exponent)
    numerator, denominator = reduce_fraction(numerator * sign, denominator)
    return 'finite', sign, numerator, denominator


def rational_to_decimal_string(num: int, den: int, digits: int = 10) -> str:
    if num == 0:
        return '0'

    sign = '-' if num < 0 else ''
    num = abs(num)
    integer_part = num // den
    remainder = num % den
    if digits == 0 or remainder == 0:
        return sign + str(integer_part)

    fractional_digits = []
    for _ in range(digits):
        remainder *= 10
        fractional_digits.append(str(remainder // den))
        remainder %= den

    fraction = ''.join(fractional_digits).rstrip('0')
    if not fraction:
        return sign + str(integer_part)
    return sign + str(integer_part) + '.' + fraction


def ieee754_to_decimal_string(bits: list, digits: int = 10) -> str:
    kind, sign, numerator, denominator = ieee754_to_rational(bits)
    if kind == 'nan':
        return 'NaN'
    if kind == 'inf':
        return '-inf' if sign < 0 else 'inf'
    return rational_to_decimal_string(numerator, denominator, digits)


def ieee754_add_sub_special(kind_a: str, sign_a: int, kind_b: str, sign_b: int, subtract: bool):
    if kind_a == 'inf' and kind_b == 'inf':
        same_sign = sign_a == sign_b
        if subtract:
            same_sign = sign_a != sign_b
        return ieee754_inf(sign_a) if same_sign else ieee754_nan()
    if kind_a == 'inf':
        return ieee754_inf(sign_a)
    if kind_b == 'inf':
        return ieee754_inf(sign_b if not subtract else -sign_b)
    return None


def ieee754_add_sub_parts(
    kind_a: str, sign_a: int, num_a: int, den_a: int,
    kind_b: str, sign_b: int, num_b: int, den_b: int, subtract: bool
) -> list:
    special = ieee754_add_sub_special(kind_a, sign_a, kind_b, sign_b, subtract)
    if special is not None:
        return special
    right_num = -num_b if subtract else num_b
    return ieee754_from_rational(num_a * den_b + right_num * den_a, den_a * den_b)


def ieee754_mul_special(kind_a: str, sign_a: int, kind_b: str, sign_b: int):
    if (kind_a == 'inf' and kind_b == 'zero') or (kind_b == 'inf' and kind_a == 'zero'):
        return ieee754_nan()
    if kind_a == 'inf' or kind_b == 'inf':
        return ieee754_inf(sign_a * sign_b)
    return None


def ieee754_mul_parts(kind_a: str, sign_a: int, num_a: int, den_a: int, kind_b: str, sign_b: int, num_b: int, den_b: int):
    special = ieee754_mul_special(kind_a, sign_a, kind_b, sign_b)
    if special is not None:
        return special
    return ieee754_from_rational(num_a * num_b, den_a * den_b)


def ieee754_div_special(kind_a: str, sign_a: int, kind_b: str, sign_b: int):
    if (kind_a == 'zero' and kind_b == 'zero') or (kind_a == 'inf' and kind_b == 'inf'):
        return ieee754_nan()
    if kind_a == 'inf':
        return ieee754_inf(sign_a * sign_b)
    if kind_b == 'inf' or kind_a == 'zero':
        return zero_bits()
    if kind_b == 'zero':
        return ieee754_inf(sign_a * sign_b)
    return None


def ieee754_div_parts(kind_a: str, sign_a: int, num_a: int, den_a: int, kind_b: str, sign_b: int, num_b: int, den_b: int):
    special = ieee754_div_special(kind_a, sign_a, kind_b, sign_b)
    if special is not None:
        return special
    return ieee754_from_rational(num_a * den_b, den_a * num_b)


def ieee754_binary_operation(a: list, b: list, operation: str) -> list:
    kind_a, sign_a, num_a, den_a = ieee754_to_rational(a)
    kind_b, sign_b, num_b, den_b = ieee754_to_rational(b)
    if kind_a == 'nan' or kind_b == 'nan':
        return ieee754_nan()
    if operation == 'add':
        return ieee754_add_sub_parts(kind_a, sign_a, num_a, den_a, kind_b, sign_b, num_b, den_b, False)
    if operation == 'sub':
        return ieee754_add_sub_parts(kind_a, sign_a, num_a, den_a, kind_b, sign_b, num_b, den_b, True)
    if operation == 'mul':
        return ieee754_mul_parts(kind_a, sign_a, num_a, den_a, kind_b, sign_b, num_b, den_b)
    if operation == 'div':
        return ieee754_div_parts(kind_a, sign_a, num_a, den_a, kind_b, sign_b, num_b, den_b)
    raise ValueError('Неизвестная операция.')


def ieee754_add(a: list, b: list) -> list:
    return ieee754_binary_operation(a, b, 'add')


def ieee754_sub(a: list, b: list) -> list:
    return ieee754_binary_operation(a, b, 'sub')


def ieee754_mul(a: list, b: list) -> list:
    return ieee754_binary_operation(a, b, 'mul')


def ieee754_div(a: list, b: list) -> list:
    return ieee754_binary_operation(a, b, 'div')


def digit_to_excess3(digit: int) -> list:
    value = digit + 3
    return [
        (value >> 3) & 1,
        (value >> 2) & 1,
        (value >> 1) & 1,
        value & 1,
    ]


def excess3_add(a: int, b: int) -> list:
    left = str(abs(a))
    right = str(abs(b))
    width = max(len(left), len(right))
    left = left.zfill(width)
    right = right.zfill(width)

    carry = 0
    result = []
    for index in range(width - 1, -1, -1):
        total = int(left[index]) + int(right[index]) + carry
        if total >= 10:
            total -= 10
            carry = 1
        else:
            carry = 0
        result.insert(0, digit_to_excess3(total))

    if carry:
        result.insert(0, digit_to_excess3(1))

    return result
