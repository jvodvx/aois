from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


VARIABLES = ("a", "b", "c", "d", "e")

TruthRow = tuple[dict[str, int], int]


class ParseError(ValueError):
    pass


@dataclass(frozen=True)
class Node:
    def evaluate(self, values: Dict[str, int]) -> int:
        raise NotImplementedError


@dataclass(frozen=True)
class ConstNode(Node):
    value: int

    def evaluate(self, values: Dict[str, int]) -> int:
        return self.value


@dataclass(frozen=True)
class VarNode(Node):
    name: str

    def evaluate(self, values: Dict[str, int]) -> int:
        return values[self.name]


@dataclass(frozen=True)
class NotNode(Node):
    operand: Node

    def evaluate(self, values: Dict[str, int]) -> int:
        return 1 - self.operand.evaluate(values)


@dataclass(frozen=True)
class BinaryNode(Node):
    operator: str
    left: Node
    right: Node

    def evaluate(self, values: Dict[str, int]) -> int:
        left = self.left.evaluate(values)
        right = self.right.evaluate(values)
        if self.operator == "&":
            return left & right
        if self.operator == "|":
            return left | right
        if self.operator == "->":
            return int((not left) or right)
        if self.operator == "~":
            return int(left == right)
        raise ValueError(f"Unsupported operator: {self.operator}")


@dataclass(frozen=True)
class ParsedExpression:
    normalized: str
    tokens: list[str]
    variables: list[str]
    root: Node


@dataclass(frozen=True)
class Implicant:
    pattern: tuple[Optional[int], ...]
    minterms: frozenset[int]

    def literal_count(self) -> int:
        return sum(bit is not None for bit in self.pattern)

    def covers(self, minterm: int, variables_count: int) -> bool:
        bits = format(minterm, f"0{variables_count}b")
        for bit, required in zip(bits, self.pattern):
            if required is None:
                continue
            if int(bit) != required:
                return False
        return True

    def can_combine(self, other: "Implicant") -> bool:
        diffs = 0
        for left, right in zip(self.pattern, other.pattern):
            if left != right:
                if left is None or right is None:
                    return False
                diffs += 1
        return diffs == 1

    def combine(self, other: "Implicant") -> "Implicant":
        pattern = tuple(left if left == right else None for left, right in zip(self.pattern, other.pattern))
        return Implicant(pattern, self.minterms | other.minterms)


@dataclass(frozen=True)
class CombinationStep:
    left: Implicant
    right: Implicant
    result: Implicant


@dataclass(frozen=True)
class GluingStage:
    source: list[Implicant]
    combinations: list[CombinationStep]
    result: list[Implicant]
    primes: list[Implicant]


@dataclass(frozen=True)
class KMapTable:
    layer: Optional[str]
    layers: list[str]
    row_vars: list[str]
    col_vars: list[str]
    rows: list[tuple[str, list[str]]]
    col_labels: list[str]
