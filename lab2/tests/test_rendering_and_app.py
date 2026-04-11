import unittest

from boolean_logic.minimization import quine_mccluskey_stages, select_minimal_cover
from boolean_logic.models import CombinationStep, Implicant
from boolean_logic.app import analyze_expression, build_analysis_sections
from boolean_logic.models import GluingStage
from boolean_logic.rendering import (
    format_index_set,
    format_table,
    render_gluing_stages,
    render_kmaps,
    render_post_classes,
    render_truth_table,
)


class RenderingAndAppTests(unittest.TestCase):
    def test_format_helpers(self) -> None:
        self.assertEqual(format_index_set([1, 2, 3]), "(1, 2, 3)")
        table = format_table(["A", "B"], [["1", "2"]])
        self.assertIn("A | B", table)

    def test_render_truth_table_and_post_classes(self) -> None:
        text = render_truth_table([({"a": 0}, 0), ({"a": 1}, 1)], ["a"])
        self.assertIn("i | a | f", text)
        classes = render_post_classes({"T0": True, "T1": False})
        self.assertIn("T0: yes", classes)
        self.assertIn("T1: no", classes)

    def test_render_gluing_stages_for_constant_zero(self) -> None:
        self.assertEqual(
            render_gluing_stages([], ["a"]),
            "Function is constant 0; no gluing is needed.",
        )

    def test_render_gluing_stages_for_empty_stage(self) -> None:
        stage = GluingStage(source=[], combinations=[], result=[], primes=[])
        rendered = render_gluing_stages([stage], ["a"])
        self.assertIn("Stage 1:", rendered)
        self.assertIn("No more combinations.", rendered)

    def test_render_kmaps_for_constant(self) -> None:
        self.assertEqual(render_kmaps([1], [], []), "Constant map: 1")

    def test_render_gluing_stages_and_kmaps_with_real_data(self) -> None:
        variables = ["a", "b", "c"]
        stages, prime_implicants = quine_mccluskey_stages([3, 4, 5, 6, 7], variables)
        cover = select_minimal_cover(prime_implicants, [3, 4, 5, 6, 7], variables)
        gluing = render_gluing_stages(stages, variables)
        kmap = render_kmaps([0, 0, 0, 1, 1, 1, 1, 1], variables, cover)
        self.assertIn("Result:", gluing)
        self.assertIn("Prime implicants fixed on this stage:", gluing)
        self.assertIn("Selected groups:", kmap)

    def test_render_gluing_stages_with_explicit_combination(self) -> None:
        left = Implicant((1, 0), frozenset({2}))
        right = Implicant((1, 1), frozenset({3}))
        result = Implicant((1, None), frozenset({2, 3}))
        stage = GluingStage(
            source=[left, right],
            combinations=[CombinationStep(left, right, result)],
            result=[result],
            primes=[left],
        )
        rendered = render_gluing_stages([stage], ["a", "b"])
        self.assertIn("[2] +", rendered)
        self.assertIn("Prime implicants fixed on this stage", rendered)

    def test_build_analysis_sections_contains_all_menu_sections(self) -> None:
        sections = build_analysis_sections("a")
        self.assertEqual(
            list(sections.keys()),
            [
                "summary",
                "truth_table",
                "normal_forms",
                "numeric_forms",
                "index_form",
                "post_classes",
                "zhegalkin",
                "fictitious",
                "derivatives",
                "calculation_method",
                "calculation_tabular",
                "karnaugh",
            ],
        )
        self.assertIn("Variables: a", sections["summary"])
        self.assertIn("SDNF: a", sections["normal_forms"])

    def test_analyze_expression_renders_full_report(self) -> None:
        report = analyze_expression("a")
        self.assertIn("Summary:", report)
        self.assertIn("Truth table:", report)
        self.assertIn("Karnaugh map:", report)
