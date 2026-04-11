from __future__ import annotations

from itertools import product
from typing import Sequence

from .truth_table import assignment_from_index


def zhegalkin_coefficients(vector: Sequence[int]) -> list[int]:
    coeffs = list(vector)
    step = 1
    while step < len(coeffs):
        for index in range(len(coeffs)):
            if index & step:
                coeffs[index] ^= coeffs[index ^ step]
        step <<= 1
    return coeffs


def monomial_from_index(index: int, variables: Sequence[str]) -> str:
    if index == 0:
        return "1"
    parts = [variables[bit] for bit in range(len(variables)) if index & (1 << (len(variables) - bit - 1))]
    return "*".join(parts)


def zhegalkin_polynomial(vector: Sequence[int], variables: Sequence[str]) -> str:
    terms = [
        monomial_from_index(index, variables)
        for index, coefficient in enumerate(zhegalkin_coefficients(vector))
        if coefficient == 1
    ]
    return " xor ".join(terms) if terms else "0"


def is_self_dual(vector: Sequence[int]) -> bool:
    size = len(vector)
    return all(vector[index] != vector[size - 1 - index] for index in range(size))


def is_monotone(vector: Sequence[int], variables: Sequence[str]) -> bool:
    max_index = 2 ** len(variables)
    for first in range(max_index):
        first_bits = assignment_from_index(first, variables)
        for second in range(max_index):
            second_bits = assignment_from_index(second, variables)
            if all(first_bits[var] <= second_bits[var] for var in variables) and vector[first] > vector[second]:
                return False
    return True


def is_linear(vector: Sequence[int]) -> bool:
    for index, coefficient in enumerate(zhegalkin_coefficients(vector)):
        if coefficient == 0 or index == 0:
            continue
        if bin(index).count("1") > 1:
            return False
    return True


def post_classes(vector: Sequence[int], variables: Sequence[str]) -> dict[str, bool]:
    if not vector:
        return {"T0": False, "T1": False, "S": False, "M": False, "L": False}
    return {
        "T0": vector[0] == 0,
        "T1": vector[-1] == 1,
        "S": is_self_dual(vector),
        "M": is_monotone(vector, variables),
        "L": is_linear(vector),
    }


def find_fictitious_variables(vector: Sequence[int], variables: Sequence[str]) -> list[str]:
    result: list[str] = []
    total = 2 ** len(variables)
    for position, variable in enumerate(variables):
        block = 2 ** (len(variables) - position - 1)
        is_fictitious = True
        for start in range(0, total, block * 2):
            for offset in range(block):
                if vector[start + offset] != vector[start + block + offset]:
                    is_fictitious = False
                    break
            if not is_fictitious:
                break
        if is_fictitious:
            result.append(variable)
    return result


def derivative_vector(vector: Sequence[int], variables: Sequence[str], by_vars: Sequence[str]) -> tuple[list[str], list[int]]:
    remaining_vars = [var for var in variables if var not in by_vars]
    if not by_vars:
        return remaining_vars, list(vector)

    results: list[int] = []
    for index in range(2 ** len(remaining_vars)):
        fixed = assignment_from_index(index, remaining_vars)
        derivative_value = 0
        for toggles in product((0, 1), repeat=len(by_vars)):
            values = dict(fixed)
            values.update({var: bit for var, bit in zip(by_vars, toggles)})
            original_index = int("".join(str(values[var]) for var in variables), 2)
            derivative_value ^= vector[original_index]
        results.append(derivative_value)
    return remaining_vars, results
