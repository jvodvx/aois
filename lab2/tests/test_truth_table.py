import unittest

from boolean_logic.parser import parse_expression
from boolean_logic.truth_table import (
    assignment_from_index,
    build_cnf_from_vector,
    build_dnf_from_vector,
    build_sdnf,
    build_sknf,
    build_truth_table,
    index_form,
    numeric_forms,
    truth_vector,
)


class TruthTableTests(unittest.TestCase):
    def test_assignment_from_index_builds_binary_mapping(self) -> None:
        self.assertEqual(assignment_from_index(5, ["a", "b", "c"]), {"a": 1, "b": 0, "c": 1})

    def test_constant_one_forms(self) -> None:
        parsed = parse_expression("1")
        rows = build_truth_table(parsed.root, parsed.variables)
        self.assertEqual(rows, [({}, 1)])
        self.assertEqual(build_sdnf(rows, parsed.variables), "1")
        self.assertEqual(build_sknf(rows, parsed.variables), "1")

    def test_forms_for_single_variable(self) -> None:
        parsed = parse_expression("a")
        rows = build_truth_table(parsed.root, parsed.variables)
        vector = truth_vector(rows)
        self.assertEqual(build_sdnf(rows, parsed.variables), "a")
        self.assertEqual(build_sknf(rows, parsed.variables), "(a)")
        self.assertEqual(numeric_forms(vector), ([1], [0]))
        self.assertEqual(index_form(vector), ("01", 1))

    def test_vector_to_forms_helpers(self) -> None:
        self.assertEqual(build_dnf_from_vector([1, 0], ["a"]), "!a")
        self.assertEqual(build_cnf_from_vector([1, 0], ["a"]), "(!a)")

    def test_sdnf_for_zero_function_is_zero(self) -> None:
        parsed = parse_expression("0")
        rows = build_truth_table(parsed.root, parsed.variables)
        self.assertEqual(build_sdnf(rows, parsed.variables), "0")
