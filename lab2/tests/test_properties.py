import unittest

from boolean_logic.properties import (
    derivative_vector,
    find_fictitious_variables,
    post_classes,
    zhegalkin_coefficients,
    zhegalkin_polynomial,
)


class PropertiesTests(unittest.TestCase):
    def test_zhegalkin_coefficients_and_polynomial(self) -> None:
        vector = [0, 0, 1, 1]
        self.assertEqual(zhegalkin_coefficients(vector), [0, 0, 1, 0])
        self.assertEqual(zhegalkin_polynomial(vector, ["a", "b"]), "a")

    def test_post_classes_for_single_variable(self) -> None:
        self.assertEqual(
            post_classes([0, 1], ["a"]),
            {"T0": True, "T1": True, "S": True, "M": True, "L": True},
        )

    def test_fictitious_variable_detection(self) -> None:
        self.assertEqual(find_fictitious_variables([0, 0, 1, 1], ["a", "b"]), ["b"])

    def test_derivative_vector_for_and_function(self) -> None:
        remaining, derivative = derivative_vector([0, 0, 0, 1], ["a", "b"], ["a"])
        self.assertEqual(remaining, ["b"])
        self.assertEqual(derivative, [0, 1])

    def test_mixed_derivative_can_reduce_to_constant(self) -> None:
        remaining, derivative = derivative_vector([0, 0, 0, 1], ["a", "b"], ["a", "b"])
        self.assertEqual(remaining, [])
        self.assertEqual(derivative, [1])

    def test_derivative_without_variables_returns_original_vector(self) -> None:
        remaining, derivative = derivative_vector([0, 1], ["a"], [])
        self.assertEqual(remaining, ["a"])
        self.assertEqual(derivative, [0, 1])

    def test_post_classes_for_empty_vector(self) -> None:
        self.assertEqual(
            post_classes([], []),
            {"T0": False, "T1": False, "S": False, "M": False, "L": False},
        )

    def test_post_classes_detect_non_monotone_and_nonlinear_function(self) -> None:
        classes = post_classes([0, 1, 1, 0], ["a", "b"])
        self.assertFalse(classes["M"])
        self.assertFalse(classes["T1"])
