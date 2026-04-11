import unittest

from boolean_logic.models import BinaryNode, ConstNode, Implicant, Node, NotNode, VarNode


class ModelTests(unittest.TestCase):
    def test_node_base_class_raises_not_implemented(self) -> None:
        with self.assertRaises(NotImplementedError):
            Node().evaluate({})

    def test_basic_nodes_evaluate_correctly(self) -> None:
        self.assertEqual(ConstNode(1).evaluate({}), 1)
        self.assertEqual(VarNode("a").evaluate({"a": 0}), 0)
        self.assertEqual(NotNode(ConstNode(1)).evaluate({}), 0)

    def test_binary_node_supports_all_operators(self) -> None:
        values = {"a": 1, "b": 0}
        self.assertEqual(BinaryNode("&", VarNode("a"), VarNode("b")).evaluate(values), 0)
        self.assertEqual(BinaryNode("|", VarNode("a"), VarNode("b")).evaluate(values), 1)
        self.assertEqual(BinaryNode("->", VarNode("a"), VarNode("b")).evaluate(values), 0)
        self.assertEqual(BinaryNode("~", VarNode("a"), VarNode("b")).evaluate(values), 0)

    def test_binary_node_rejects_unknown_operator(self) -> None:
        with self.assertRaises(ValueError):
            BinaryNode("^", ConstNode(1), ConstNode(0)).evaluate({})

    def test_implicant_helpers(self) -> None:
        first = Implicant((1, 0, None), frozenset({4, 5}))
        second = Implicant((1, 1, None), frozenset({6, 7}))
        third = Implicant((1, None, 1), frozenset({5, 7}))
        self.assertEqual(first.literal_count(), 2)
        self.assertTrue(first.covers(4, 3))
        self.assertTrue(first.can_combine(second))
        self.assertFalse(first.can_combine(third))
        self.assertEqual(first.combine(second), Implicant((1, None, None), frozenset({4, 5, 6, 7})))
