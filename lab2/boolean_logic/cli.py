from __future__ import annotations

from .app import analyze_expression, build_analysis_sections
from .models import ParseError


MENU_ITEMS = {
    "1": ("Show truth table", "truth_table"),
    "2": ("Show SDNF and SKNF", "normal_forms"),
    "3": ("Show numeric forms", "numeric_forms"),
    "4": ("Show index form", "index_form"),
    "5": ("Show Post classes", "post_classes"),
    "6": ("Show Zhegalkin polynomial", "zhegalkin"),
    "7": ("Show fictitious variables", "fictitious"),
    "8": ("Show Boolean derivatives", "derivatives"),
    "9": ("Minimize by calculation method", "calculation_method"),
    "10": ("Minimize by calculation-tabular method", "calculation_tabular"),
    "11": ("Minimize by Karnaugh map", "karnaugh"),
}


def prompt_expression() -> str | None:
    while True:
        try:
            expression = input("Enter boolean function: ").strip().lstrip("\ufeff")
        except EOFError:
            return None
        if expression:
            return expression
        print("Empty input. Try again.")


def print_menu(current_expression: str) -> None:
    print()
    print("=" * 72)
    print("Boolean function laboratory menu")
    print(f"Current expression: {current_expression}")
    print("-" * 72)
    print("1  - Truth table")
    print("2  - SDNF and SKNF")
    print("3  - Numeric forms")
    print("4  - Index form")
    print("5  - Post classes")
    print("6  - Zhegalkin polynomial")
    print("7  - Fictitious variables")
    print("8  - Boolean derivatives")
    print("9  - Calculation minimization")
    print("10 - Calculation-tabular minimization")
    print("11 - Karnaugh map minimization")
    print("12 - Full report")
    print("13 - Change expression")
    print("0  - Exit")
    print("=" * 72)


def print_section(title: str, content: str) -> None:
    print()
    print(title)
    print("-" * len(title))
    print(content)


def main() -> None:
    expression = prompt_expression()
    if expression is None:
        return

    while True:
        print_menu(expression)
        try:
            choice = input("Select menu item: ").strip()
        except EOFError:
            print()
            return

        if choice == "0":
            return

        if choice == "13":
            new_expression = prompt_expression()
            if new_expression is None:
                print()
                return
            expression = new_expression
            continue

        try:
            if choice == "12":
                print()
                print(analyze_expression(expression))
                continue

            if choice not in MENU_ITEMS:
                print("Unknown menu item.")
                continue

            title, section_key = MENU_ITEMS[choice]
            sections = build_analysis_sections(expression)
            print_section(title, sections[section_key])
        except ParseError as error:
            print(f"Parse error: {error}")
            new_expression = prompt_expression()
            if new_expression is None:
                print()
                return
            expression = new_expression
        except Exception as error:
            print(f"Error: {error}")
