import unittest

from boolean_logic.models import ParseError
from boolean_logic.parser import parse_expression
from boolean_logic.truth_table import build_truth_table, truth_vector


class ParserTests(unittest.TestCase):
    def test_parse_expression_normalizes_symbols(self) -> None:
        parsed = parse_expression(" !(!a→!b) ∨ c ")
        self.assertEqual(parsed.normalized, "!(!a->!b)|c")
        self.assertEqual(parsed.variables, ["a", "b", "c"])

    def test_operator_precedence_matches_truth_vector(self) -> None:
        parsed = parse_expression("a|b&c")
        vector = truth_vector(build_truth_table(parsed.root, parsed.variables))
        self.assertEqual(vector, [0, 0, 0, 1, 1, 1, 1, 1])

    def test_implication_is_right_associative(self) -> None:
        parsed = parse_expression("0->1->0")
        self.assertEqual(parsed.root.evaluate({}), 1)

    def test_invalid_symbol_raises_parse_error(self) -> None:
        with self.assertRaises(ParseError):
            parse_expression("a@b")

    def test_empty_expression_raises_parse_error(self) -> None:
        with self.assertRaises(ParseError):
            parse_expression("")

    def test_unexpected_remaining_token_raises_parse_error(self) -> None:
        with self.assertRaises(ParseError):
            parse_expression("a)")

    def test_missing_closing_bracket_raises_parse_error(self) -> None:
        with self.assertRaises(ParseError):
            parse_expression("(a")

    def test_unexpected_end_after_negation_raises_parse_error(self) -> None:
        with self.assertRaises(ParseError):
            parse_expression("!")

    def test_unexpected_token_inside_unary_parser_raises_parse_error(self) -> None:
        with self.assertRaises(ParseError):
            parse_expression(")")

    def test_equivalence_operator_is_supported(self) -> None:
        parsed = parse_expression("a~b~c")
        self.assertEqual(parsed.variables, ["a", "b", "c"])
