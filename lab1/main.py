from bitmath_impl import *

def input_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except:
            print("Ошибка: введите целое число.")

def print_bits(bits: list):
    print("".join(str(b) for b in bits))

def print_division_result(result):
    if result is None:
        print("Ошибка: деление на ноль.")
        return
    sign, q, frac = result
    s = "-" if sign == 1 else ""
    print(s + str(q) + "." + "".join(str(x) for x in frac))

def task1():
    n = input_int("Введите целое число: ")
    direct = dec_to_direct(n)
    ones = direct_to_ones(direct)
    twos = direct_to_twos(direct)
    print("\nПрямой код:"); print_bits(direct)
    print("Обратный код:"); print_bits(ones)
    print("Дополнительный код:"); print_bits(twos)

def task2():
    a = input_int("Введите A: ")
    b = input_int("Введите B: ")
    A = direct_to_twos(dec_to_direct(a))
    B = direct_to_twos(dec_to_direct(b))
    res = add_twos(A, B)
    print("\nРезультат (доп. код):"); print_bits(res)
    print("В десятичном виде:", twos_to_dec(res))

def task3():
    a = input_int("Введите A: ")
    b = input_int("Введите B: ")
    A = direct_to_twos(dec_to_direct(a))
    B = direct_to_twos(dec_to_direct(b))
    negB = negate_twos(B)
    res = add_twos(A, negB)
    print("\nA - B (доп. код):"); print_bits(res)
    print("В десятичном виде:", twos_to_dec(res))

def task4():
    a = input_int("Введите A: ")
    b = input_int("Введите B: ")
    A = dec_to_direct(a)
    B = dec_to_direct(b)
    res = mul_direct(A, B)
    print("\nРезультат (прямой код):"); print_bits(res)
    print("В десятичном виде:", twos_to_dec(direct_to_twos(res)))

def task5():
    a = input_int("Введите A: ")
    b = input_int("Введите B: ")
    A = dec_to_direct(a)
    B = dec_to_direct(b)
    result = div_direct(A, B)
    print("\nРезультат деления:")
    print_division_result(result)

def task6():
    n = input_int("Введите целое число: ")
    bits = ieee754_from_int(n)
    print("\nIEEE-754 (32 бита):"); print_bits(bits)

def task7():
    a = input_int("Введите A (десятичное): ")
    b = input_int("Введите B (десятичное): ")
    res = excess3_add(a, b)
    print("\nРезультат в Excess-3:")
    for digit in res:
        print("".join(str(x) for x in digit), end=" ")
    print()

def show_menu():
    print("\nЛАБОРАТОРНАЯ: ПРЕДСТАВЛЕНИЕ ЧИСЕЛ")
    print("1  — Перевод в прямой / обратный / доп. код")
    print("2  — Сложение (дополнительный код)")
    print("3  — Вычитание через отрицание")
    print("4  — Умножение (прямой код)")
    print("5  — Деление (прямой код, 5 знаков)")
    print("6  — IEEE-754 (32 бита)")
    print("7  — Сложение в Excess-3 BCD")
    print("0  — Выход")

def main():
    tasks = {
        '1': task1,
        '2': task2,
        '3': task3,
        '4': task4,
        '5': task5,
        '6': task6,
        '7': task7,
    }
    while True:
        show_menu()
        choice = input("Выберите пункт меню: ")
        if choice == '0':
            print("Выход из программы.")
            break
        func = tasks.get(choice)
        if func:
            func()
        else:
            print("Неверный пункт меню.")

if __name__ == "__main__":
    main()