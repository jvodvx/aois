from bitmath_impl import *


def input_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите целое число.")


def input_decimal(prompt: str) -> str:
    while True:
        value = input(prompt)
        try:
            parse_decimal(value)
            return value
        except ValueError:
            print("Ошибка: введите число в десятичном формате.")


def print_bits(bits: list):
    print("".join(str(bit) for bit in bits))


def format_division_binary(result) -> str:
    sign, integer_part, fraction_bits = result
    integer_bits = dec_to_direct(integer_part)
    integer_bits[0] = sign if integer_part != 0 or any(fraction_bits) else 0
    return f"{''.join(str(bit) for bit in integer_bits)}.{''.join(str(bit) for bit in fraction_bits)}"


def format_division_decimal(result) -> str:
    sign, integer_part, fraction_bits = result
    fractional_value = 0
    fractional_denominator = 1
    for bit in fraction_bits:
        fractional_value = fractional_value * 2 + bit
        fractional_denominator *= 2
    numerator = integer_part * fractional_denominator + fractional_value
    if sign == 1:
        numerator = -numerator
    return fixed_decimal_string(numerator, fractional_denominator, 5)


def fixed_decimal_string(num: int, den: int, digits: int) -> str:
    sign = '-' if num < 0 else ''
    num = abs(num)
    integer_part = num // den
    remainder = num % den
    fraction = []
    for _ in range(digits):
        remainder *= 10
        fraction.append(str(remainder // den))
        remainder %= den
    return sign + str(integer_part) + ',' + ''.join(fraction)


def print_ieee_result(label: str, bits: list):
    print(f"\n{label}")
    print("Двоичный вид:")
    print_bits(bits)
    print("Десятичный вид:", ieee754_to_decimal_string(bits, 10))


def choose_ieee_operation():
    operations = {
        '1': ('A + B', ieee754_add),
        '2': ('A - B', ieee754_sub),
        '3': ('A * B', ieee754_mul),
        '4': ('A / B', ieee754_div),
    }

    print("\nОперации IEEE-754")
    print("1  - Сложение")
    print("2  - Вычитание")
    print("3  - Умножение")
    print("4  - Деление")
    print("5  - Выполнить все операции")

    while True:
        choice = input("Выберите операцию: ")
        if choice == '5':
            return None
        selected = operations.get(choice)
        if selected is not None:
            return selected
        print("Неверный пункт меню.")


def task1():
    number = input_int("Введите целое число: ")
    direct = dec_to_direct(number)
    ones = direct_to_ones(direct)
    twos = direct_to_twos(direct)
    print("\nПрямой код:")
    print_bits(direct)
    print("Обратный код:")
    print_bits(ones)
    print("Дополнительный код:")
    print_bits(twos)
    print("Десятичное число:", number)


def task2():
    left = input_int("Введите A: ")
    right = input_int("Введите B: ")
    left_bits = direct_to_twos(dec_to_direct(left))
    right_bits = direct_to_twos(dec_to_direct(right))
    result = add_twos(left_bits, right_bits)
    print("\nРезультат сложения в дополнительном коде:")
    print_bits(result)
    print("В десятичном виде:", twos_to_dec(result))


def task3():
    left = input_int("Введите A: ")
    right = input_int("Введите B: ")
    left_bits = direct_to_twos(dec_to_direct(left))
    right_bits = direct_to_twos(dec_to_direct(right))
    result = add_twos(left_bits, negate_twos(right_bits))
    print("\nРезультат вычитания в дополнительном коде:")
    print_bits(result)
    print("В десятичном виде:", twos_to_dec(result))


def task4():
    left = input_int("Введите A: ")
    right = input_int("Введите B: ")
    result = mul_direct(dec_to_direct(left), dec_to_direct(right))
    print("\nРезультат умножения в прямом коде:")
    print_bits(result)
    print("В десятичном виде:", twos_to_dec(direct_to_twos(result)))


def task5():
    left = input_int("Введите A: ")
    right = input_int("Введите B: ")
    result = div_direct(dec_to_direct(left), dec_to_direct(right))
    if result is None:
        print("\nОшибка: деление на ноль.")
        return
    print("\nРезультат деления в двоичном виде:")
    print(format_division_binary(result))
    print("В десятичном виде:", format_division_decimal(result))


def task6():
    value = input_decimal("Введите десятичное число: ")
    bits = ieee754_from_decimal(value)
    print_ieee_result("Число в IEEE-754 (32 бита):", bits)


def task7():
    left = input_decimal("Введите A: ")
    right = input_decimal("Введите B: ")
    left_bits = ieee754_from_decimal(left)
    right_bits = ieee754_from_decimal(right)
    selected_operation = choose_ieee_operation()

    print_ieee_result("A в IEEE-754 (32 бита):", left_bits)
    print_ieee_result("B в IEEE-754 (32 бита):", right_bits)

    if selected_operation is None:
        print_ieee_result("A + B:", ieee754_add(left_bits, right_bits))
        print_ieee_result("A - B:", ieee754_sub(left_bits, right_bits))
        print_ieee_result("A * B:", ieee754_mul(left_bits, right_bits))
        print_ieee_result("A / B:", ieee754_div(left_bits, right_bits))
        return

    label, operation = selected_operation
    print_ieee_result(label + ":", operation(left_bits, right_bits))


def task8():
    left = input_int("Введите A (десятичное): ")
    right = input_int("Введите B (десятичное): ")
    result = excess3_add(left, right)
    print("\nРезультат в Excess-3:")
    print(" ".join("".join(str(bit) for bit in digit) for digit in result))
    print("В десятичном виде:", left + right)


def show_menu():
    print("\nЛАБОРАТОРНАЯ: ПРЕДСТАВЛЕНИЕ ЧИСЕЛ")
    print("1  - Перевод в прямой / обратный / дополнительный код")
    print("2  - Сложение в дополнительном коде")
    print("3  - Вычитание через отрицание")
    print("4  - Умножение в прямом коде")
    print("5  - Деление в прямом коде (5 двоичных знаков)")
    print("6  - Перевод числа в IEEE-754 (32 бита)")
    print("7  - Операции IEEE-754 (32 бита)")
    print("8  - Сложение в Excess-3")
    print("0  - Выход")


def main():
    tasks = {
        '1': task1,
        '2': task2,
        '3': task3,
        '4': task4,
        '5': task5,
        '6': task6,
        '7': task7,
        '8': task8,
    }

    while True:
        show_menu()
        choice = input("Выберите пункт меню: ")
        if choice == '0':
            print("Выход из программы.")
            break

        task = tasks.get(choice)
        if task is None:
            print("Неверный пункт меню.")
            continue
        task()


if __name__ == "__main__":
    main()
