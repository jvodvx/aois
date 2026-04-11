import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from boolean_logic import cli


class CliTests(unittest.TestCase):
    def test_prompt_expression_retries_and_strips_bom(self) -> None:
        with patch("builtins.input", side_effect=["", "\ufeffa"]):
            with io.StringIO() as buffer, redirect_stdout(buffer):
                expression = cli.prompt_expression()
                output = buffer.getvalue()
        self.assertEqual(expression, "a")
        self.assertIn("Empty input. Try again.", output)

    def test_main_shows_selected_section(self) -> None:
        with patch("builtins.input", side_effect=["a", "2", "0"]):
            with io.StringIO() as buffer, redirect_stdout(buffer):
                cli.main()
                output = buffer.getvalue()
        self.assertIn("Show SDNF and SKNF", output)
        self.assertIn("SDNF: a", output)

    def test_main_can_change_expression_and_show_full_report(self) -> None:
        with patch("builtins.input", side_effect=["a", "13", "1", "12", "0"]):
            with io.StringIO() as buffer, redirect_stdout(buffer):
                cli.main()
                output = buffer.getvalue()
        self.assertIn("Current expression: 1", output)
        self.assertIn("Index form: 1 -> 1", output)

    def test_main_handles_parse_error_and_requests_new_expression(self) -> None:
        with patch("builtins.input", side_effect=["@", "1", "a", "0"]):
            with io.StringIO() as buffer, redirect_stdout(buffer):
                cli.main()
                output = buffer.getvalue()
        self.assertIn("Parse error:", output)
        self.assertIn("Current expression: a", output)

    def test_prompt_expression_returns_none_on_eof(self) -> None:
        with patch("builtins.input", side_effect=EOFError):
            self.assertIsNone(cli.prompt_expression())

    def test_main_returns_when_initial_expression_is_missing(self) -> None:
        with patch("builtins.input", side_effect=EOFError):
            with io.StringIO() as buffer, redirect_stdout(buffer):
                cli.main()
                output = buffer.getvalue()
        self.assertEqual(output, "")

    def test_main_handles_unknown_menu_item(self) -> None:
        with patch("builtins.input", side_effect=["a", "99", "0"]):
            with io.StringIO() as buffer, redirect_stdout(buffer):
                cli.main()
                output = buffer.getvalue()
        self.assertIn("Unknown menu item.", output)

    def test_main_returns_on_choice_eof(self) -> None:
        with patch("builtins.input", side_effect=["a", EOFError]):
            with io.StringIO() as buffer, redirect_stdout(buffer):
                cli.main()
                output = buffer.getvalue()
        self.assertTrue(output.endswith("\n"))

    def test_main_returns_when_expression_change_is_cancelled(self) -> None:
        with patch("builtins.input", side_effect=["a", "13", EOFError]):
            with io.StringIO() as buffer, redirect_stdout(buffer):
                cli.main()
                output = buffer.getvalue()
        self.assertTrue(output.endswith("\n"))

    def test_main_handles_unexpected_runtime_error(self) -> None:
        with patch("builtins.input", side_effect=["a", "1", "0"]):
            with patch("boolean_logic.cli.build_analysis_sections", side_effect=RuntimeError("boom")):
                with io.StringIO() as buffer, redirect_stdout(buffer):
                    cli.main()
                    output = buffer.getvalue()
        self.assertIn("Error: boom", output)
