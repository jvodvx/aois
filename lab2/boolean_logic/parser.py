from __future__ import annotations

from typing import Optional, Sequence

from .models import BinaryNode, ConstNode, Node, NotNode, ParseError, ParsedExpression, VARIABLES, VarNode


def normalize_expression(expression: str) -> str:
    replacements = {
        " ": "",
        "\t": "",
        "\n": "",
        "\r": "",
        "\ufeff": "",
        "¬": "!",
        "∧": "&",
        "^": "&",
        "∨": "|",
        "+": "|",
        "→": "->",
        "=>": "->",
        "↔": "~",
        "≡": "~",
    }
    normalized = expression
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    return normalized


def tokenize(expression: str) -> list[str]:
    tokens: list[str] = []
    index = 0
    while index < len(expression):
        char = expression[index]
        if char in "()!&|~":
            tokens.append(char)
            index += 1
            continue
        if char == "-" and index + 1 < len(expression) and expression[index + 1] == ">":
            tokens.append("->")
            index += 2
            continue
        if char in VARIABLES or char in "01":
            tokens.append(char)
            index += 1
            continue
        raise ParseError(f"Unexpected symbol: {char!r}")
    return tokens


class Parser:
    def __init__(self, tokens: Sequence[str]) -> None:
        self.tokens = list(tokens)
        self.position = 0

    def parse(self) -> Node:
        if not self.tokens:
            raise ParseError("Empty expression.")
        node = self.parse_equivalence()
        if self.position != len(self.tokens):
            raise ParseError(f"Unexpected token: {self.tokens[self.position]!r}")
        return node

    def current(self) -> Optional[str]:
        if self.position >= len(self.tokens):
            return None
        return self.tokens[self.position]

    def consume(self, token: str) -> bool:
        if self.current() == token:
            self.position += 1
            return True
        return False

    def expect(self, token: str) -> None:
        if not self.consume(token):
            raise ParseError(f"Expected {token!r}, found {self.current()!r}")

    def parse_equivalence(self) -> Node:
        node = self.parse_implication()
        while self.consume("~"):
            node = BinaryNode("~", node, self.parse_implication())
        return node

    def parse_implication(self) -> Node:
        node = self.parse_or()
        if self.consume("->"):
            node = BinaryNode("->", node, self.parse_implication())
        return node

    def parse_or(self) -> Node:
        node = self.parse_and()
        while self.consume("|"):
            node = BinaryNode("|", node, self.parse_and())
        return node

    def parse_and(self) -> Node:
        node = self.parse_unary()
        while self.consume("&"):
            node = BinaryNode("&", node, self.parse_unary())
        return node

    def parse_unary(self) -> Node:
        if self.consume("!"):
            return NotNode(self.parse_unary())
        if self.consume("("):
            node = self.parse_equivalence()
            self.expect(")")
            return node
        token = self.current()
        if token is None:
            raise ParseError("Unexpected end of expression.")
        if token in VARIABLES:
            self.position += 1
            return VarNode(token)
        if token in ("0", "1"):
            self.position += 1
            return ConstNode(int(token))
        raise ParseError(f"Unexpected token: {token!r}")


def extract_variables(tokens: Sequence[str]) -> list[str]:
    found = sorted({token for token in tokens if token in VARIABLES}, key=VARIABLES.index)
    if len(found) > 5:
        raise ValueError("No more than five variables are supported.")
    return found


def parse_expression(expression: str) -> ParsedExpression:
    normalized = normalize_expression(expression)
    tokens = tokenize(normalized)
    return ParsedExpression(
        normalized=normalized,
        tokens=tokens,
        variables=extract_variables(tokens),
        root=Parser(tokens).parse(),
    )
