import unittest

from boolean_logic.minimization import (
    build_kmap_tables,
    cover_table,
    gray_codes,
    implicant_to_string,
    kmap_layout,
    minimized_dnf,
    quine_mccluskey_stages,
    select_minimal_cover,
    unique_patterns,
)
from boolean_logic.models import Implicant


class MinimizationTests(unittest.TestCase):
    def test_implicant_to_string_handles_partial_pattern(self) -> None:
        implicant = Implicant((1, None, 0), frozenset({4, 6}))
        self.assertEqual(implicant_to_string(implicant, ["a", "b", "c"]), "(a&!c)")

    def test_unique_patterns_merges_same_pattern(self) -> None:
        merged = unique_patterns(
            [
                Implicant((1, None), frozenset({2})),
                Implicant((1, None), frozenset({3})),
            ]
        )
        self.assertEqual(merged, [Implicant((1, None), frozenset({2, 3}))])

    def test_quine_mccluskey_minimizes_a_or_bc(self) -> None:
        variables = ["a", "b", "c"]
        stages, prime_implicants = quine_mccluskey_stages([3, 4, 5, 6, 7], variables)
        minimal_cover = select_minimal_cover(prime_implicants, [3, 4, 5, 6, 7], variables)
        self.assertEqual(len(stages), 3)
        self.assertEqual(
            {implicant_to_string(item, variables) for item in minimal_cover},
            {"a", "(b&c)"},
        )
        self.assertEqual(
            {implicant_to_string(item, variables) for item in prime_implicants},
            {"a", "(b&c)"},
        )
        self.assertIn("a", minimized_dnf(minimal_cover, variables))

    def test_quine_mccluskey_handles_zero_function(self) -> None:
        self.assertEqual(quine_mccluskey_stages([], ["a", "b"]), ([], []))
        self.assertEqual(select_minimal_cover([], [], ["a", "b"]), [])
        self.assertEqual(minimized_dnf([], ["a", "b"]), "0")

    def test_select_minimal_cover_uses_search_when_no_essential_implicants(self) -> None:
        variables = ["a", "b", "c"]
        prime_implicants = [
            Implicant((0, 0, None), frozenset({0, 1})),
            Implicant((0, None, 0), frozenset({0, 2})),
            Implicant((None, 0, 1), frozenset({1, 5})),
            Implicant((None, 1, 0), frozenset({2, 6})),
            Implicant((1, None, 1), frozenset({5, 7})),
        ]
        minterms = [0, 1, 2, 5]
        cover = select_minimal_cover(prime_implicants, minterms, variables)
        self.assertEqual(len(cover), 2)
        for minterm in minterms:
            self.assertTrue(any(implicant.covers(minterm, len(variables)) for implicant in cover))

    def test_cover_table_marks_covered_minterms(self) -> None:
        variables = ["a", "b"]
        implicants = [Implicant((1, None), frozenset({2, 3}))]
        self.assertEqual(cover_table(implicants, [2, 3], variables), [["a", "X", "X"]])

    def test_gray_codes_and_kmap_layout_variants(self) -> None:
        self.assertEqual(gray_codes(0), [""])
        self.assertEqual(gray_codes(1), ["0", "1"])
        self.assertEqual(gray_codes(2), ["00", "01", "11", "10"])
        self.assertEqual(kmap_layout([]), ([], [], []))
        self.assertEqual(kmap_layout(["a"]), ([], [], ["a"]))
        self.assertEqual(kmap_layout(["a", "b"]), ([], ["a"], ["b"]))
        self.assertEqual(kmap_layout(["a", "b", "c"]), ([], ["a"], ["b", "c"]))
        self.assertEqual(kmap_layout(["a", "b", "c", "d"]), ([], ["a", "b"], ["c", "d"]))
        self.assertEqual(kmap_layout(["a", "b", "c", "d", "e"]), (["a"], ["b", "c"], ["d", "e"]))

    def test_build_kmap_tables_for_five_variables(self) -> None:
        tables = build_kmap_tables([0] * 32, ["a", "b", "c", "d", "e"])
        self.assertEqual(len(tables), 2)
        self.assertEqual(len(tables[0].rows), 4)
        self.assertEqual(len(tables[0].col_labels), 4)
