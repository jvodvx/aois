from bitmath_decl import BITS

EXP_BITS = 8
MANTISSA_BITS = 23
BIAS = 127
MANTISSA_START = 9
DIV_PRECISION = 5


def zero_bits():
    return [0] * BITS


def copy_bits(a):
    return [a[i] for i in range(BITS)]


def dec_to_binary_unsigned(n):
    bits = zero_bits()
    i = BITS - 1
    while n > 0 and i >= 0:
        bits[i] = n % 2
        n //= 2
        i -= 1
    return bits


def dec_to_direct(n: int) -> list:
    bits = zero_bits()
    if n < 0:
        bits[0] = 1
        n = -n
    mag = dec_to_binary_unsigned(n)
    for i in range(1, BITS):
        bits[i] = mag[i]
    return bits


def direct_to_ones(bits: list) -> list:
    res = copy_bits(bits)
    if bits[0] == 1:
        for i in range(1, BITS):
            res[i] = 1 - res[i]
    return res


def ones_to_twos(bits: list) -> list:
    res = copy_bits(bits)
    carry = 1
    for i in range(BITS - 1, -1, -1):
        s = res[i] + carry
        res[i] = s % 2
        carry = s // 2
    return res


def direct_to_twos(bits: list) -> list:
    if bits[0] == 0:
        return copy_bits(bits)
    return ones_to_twos(direct_to_ones(bits))


def add_twos(a: list, b: list) -> list:
    res = zero_bits()
    carry = 0
    for i in range(BITS - 1, -1, -1):
        s = a[i] + b[i] + carry
        res[i] = s % 2
        carry = s // 2
    return res


def negate_twos(bits: list) -> list:
    inv = [1 - bits[i] for i in range(BITS)]
    return ones_to_twos(inv)


def twos_to_dec(bits: list) -> int:
    if bits[0] == 1 and all(b == 0 for b in bits[1:]):
        return -2 ** (BITS - 1)

    if bits[0] == 0:
        val = 0
        for i in range(1, BITS):
            val = val * 2 + bits[i]
        return val
    else:
        neg = negate_twos(bits)
        val = 0
        for i in range(1, BITS):
            val = val * 2 + neg[i]
        return -val


def shift_left(bits, k):
    """Сдвиг массива влево на k бит (заполнение нулями справа). Бит 0 – самый старший."""
    res = zero_bits()
    for i in range(k, BITS):
        res[i - k] = bits[i]
    return res


def mul_direct(a: list, b: list) -> list:
    sign = a[0] ^ b[0]

    x = zero_bits()
    y = zero_bits()
    for i in range(1, BITS):
        x[i] = a[i]
        y[i] = b[i]

    result = zero_bits()

    for i in range(BITS - 1, 0, -1):
        if y[i] == 1:
            shifted = shift_left(x, BITS - 1 - i)
            result = add_twos(result, shifted)

    result[0] = sign
    return result

def abs_ge(a, b):
    """Сравнение беззнаковых массивов a и b (бит 0 – самый старший). Возвращает True, если a >= b."""
    for i in range(BITS):
        if a[i] > b[i]:
            return True
        if a[i] < b[i]:
            return False
    return True


def abs_sub(a, b):
    res = zero_bits()
    borrow = 0
    for i in range(BITS - 1, -1, -1):
        diff = a[i] - b[i] - borrow
        if diff < 0:
            diff += 2
            borrow = 1
        else:
            borrow = 0
        res[i] = diff
    return res


def div_direct(a: list, b: list):
    sign = a[0] ^ b[0]

    dividend = zero_bits()
    divisor = zero_bits()
    for i in range(1, BITS):
        dividend[i] = a[i]
        divisor[i] = b[i]

    if all(divisor[i] == 0 for i in range(1, BITS)):
        return None

    quotient = zero_bits()
    remainder = zero_bits()

    for i in range(1, BITS):
        remainder = shift_left(remainder, 1)
        remainder[BITS - 1] = dividend[i]

        if abs_ge(remainder, divisor):
            remainder = abs_sub(remainder, divisor)
            quotient = shift_left(quotient, 1)
            quotient[BITS - 1] = 1
        else:
            quotient = shift_left(quotient, 1)
            quotient[BITS - 1] = 0

    frac = []
    for _ in range(DIV_PRECISION):
        remainder = shift_left(remainder, 1)
        if abs_ge(remainder, divisor):
            remainder = abs_sub(remainder, divisor)
            frac.append(1)
        else:
            frac.append(0)

    int_part = twos_to_dec(quotient)

    return sign, int_part, frac


def ieee754_from_int(n: int) -> list:
    bits = zero_bits()
    if n == 0:
        return bits
    if n < 0:
        bits[0] = 1
        n = -n

    bin_n = []
    while n > 0:
        bin_n.append(n % 2)
        n //= 2
    bin_n.reverse()

    exp = len(bin_n) - 1
    exp_bias = exp + BIAS

    for i in range(EXP_BITS):
        bits[1 + i] = (exp_bias // (2 ** (EXP_BITS - 1 - i))) % 2

    for i in range(MANTISSA_BITS):
        if i + 1 < len(bin_n):
            bits[MANTISSA_START + i] = bin_n[i + 1]
        else:
            bits[MANTISSA_START + i] = 0

    return bits


def digit_to_excess3(d):
    b = d + 3
    return [
        (b >> 3) & 1,
        (b >> 2) & 1,
        (b >> 1) & 1,
        b & 1
    ]


def excess3_add(a: int, b: int) -> list:
    sa = str(a)
    sb = str(b)
    n = max(len(sa), len(sb))
    sa = sa.zfill(n)
    sb = sb.zfill(n)

    carry = 0
    result = []

    for i in range(n - 1, -1, -1):
        digit_a = int(sa[i])
        digit_b = int(sb[i])

        s = digit_a + digit_b + carry
        if s >= 10:
            s -= 10
            carry = 1
        else:
            carry = 0

        result.insert(0, digit_to_excess3(s))

    if carry:
        result.insert(0, digit_to_excess3(1))

    return result