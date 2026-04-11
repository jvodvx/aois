from __future__ import annotations

from typing import Sequence

from .models import Node, TruthRow


def assignment_from_index(index: int, variables: Sequence[str]) -> dict[str, int]:
    bit_string = format(index, f"0{len(variables)}b")
    return {var: int(bit) for var, bit in zip(variables, bit_string)}


def build_truth_table(root: Node, variables: Sequence[str]) -> list[TruthRow]:
    rows: list[TruthRow] = []
    for index in range(2 ** len(variables)):
        values = assignment_from_index(index, variables)
        rows.append((values, root.evaluate(values)))
    return rows


def truth_vector(rows: Sequence[TruthRow]) -> list[int]:
    return [value for _, value in rows]


def build_minterm(values: dict[str, int], variables: Sequence[str]) -> str:
    literals = [var if values[var] == 1 else f"!{var}" for var in variables]
    return "&".join(literals) if literals else "1"


def build_maxterm(values: dict[str, int], variables: Sequence[str]) -> str:
    literals = [var if values[var] == 0 else f"!{var}" for var in variables]
    return "(" + "|".join(literals) + ")" if literals else "0"


def build_sdnf(rows: Sequence[TruthRow], variables: Sequence[str]) -> str:
    terms = [build_minterm(values, variables) for values, value in rows if value == 1]
    if not terms:
        return "0"
    return " | ".join(f"({term})" if "&" in term else term for term in terms)


def build_sknf(rows: Sequence[TruthRow], variables: Sequence[str]) -> str:
    terms = [build_maxterm(values, variables) for values, value in rows if value == 0]
    if not terms:
        return "1"
    return " & ".join(terms)


def numeric_forms(vector: Sequence[int]) -> tuple[list[int], list[int]]:
    ones = [index for index, value in enumerate(vector) if value == 1]
    zeros = [index for index, value in enumerate(vector) if value == 0]
    return ones, zeros


def index_form(vector: Sequence[int]) -> tuple[str, int]:
    bit_string = "".join(map(str, vector)) or "0"
    return bit_string, int(bit_string, 2)


def build_dnf_from_vector(vector: Sequence[int], variables: Sequence[str]) -> str:
    rows = [(assignment_from_index(index, variables), value) for index, value in enumerate(vector)]
    return build_sdnf(rows, variables)


def build_cnf_from_vector(vector: Sequence[int], variables: Sequence[str]) -> str:
    rows = [(assignment_from_index(index, variables), value) for index, value in enumerate(vector)]
    return build_sknf(rows, variables)
