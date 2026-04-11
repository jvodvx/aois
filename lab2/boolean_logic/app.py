from __future__ import annotations

from collections import OrderedDict

from .minimization import cover_table, minimized_dnf, quine_mccluskey_stages, select_minimal_cover
from .parser import parse_expression
from .properties import find_fictitious_variables, post_classes, zhegalkin_polynomial
from .rendering import (
    format_index_set,
    format_table,
    render_derivatives,
    render_gluing_stages,
    render_kmaps,
    render_post_classes,
    render_truth_table,
)
from .truth_table import build_sdnf, build_sknf, build_truth_table, index_form, numeric_forms, truth_vector


def build_analysis_sections(expression: str) -> OrderedDict[str, str]:
    parsed = parse_expression(expression)
    rows = build_truth_table(parsed.root, parsed.variables)
    vector = truth_vector(rows)
    ones, zeros = numeric_forms(vector)
    bit_string, index_number = index_form(vector)
    classes = post_classes(vector, parsed.variables)
    fictitious = find_fictitious_variables(vector, parsed.variables)
    stages, prime_implicants = quine_mccluskey_stages(ones, parsed.variables)
    minimal_cover = select_minimal_cover(prime_implicants, ones, parsed.variables)
    chart = cover_table(prime_implicants, ones, parsed.variables)

    sections: OrderedDict[str, str] = OrderedDict()
    sections["summary"] = "\n".join(
        [
            f"Expression: {parsed.normalized}",
            f"Variables: {', '.join(parsed.variables) if parsed.variables else '-'}",
        ]
    )
    sections["truth_table"] = render_truth_table(rows, parsed.variables)
    sections["normal_forms"] = "\n".join(
        [
            f"SDNF: {build_sdnf(rows, parsed.variables)}",
            f"SKNF: {build_sknf(rows, parsed.variables)}",
        ]
    )
    sections["numeric_forms"] = "\n".join(
        [
            f"Numeric SDNF: Sigma{format_index_set(ones)}",
            f"Numeric SKNF: Pi{format_index_set(zeros)}",
        ]
    )
    sections["index_form"] = f"Index form: {bit_string} -> {index_number}"
    sections["post_classes"] = render_post_classes(classes)
    sections["zhegalkin"] = f"Zhegalkin polynomial: {zhegalkin_polynomial(vector, parsed.variables)}"
    sections["fictitious"] = f"Fictitious variables: {', '.join(fictitious) if fictitious else 'none'}"
    sections["derivatives"] = render_derivatives(vector, parsed.variables)
    sections["calculation_method"] = "\n".join(
        [
            render_gluing_stages(stages, parsed.variables),
            f"Prime implicants: {minimized_dnf(prime_implicants, parsed.variables) if prime_implicants else '0'}",
            f"Minimal DNF: {minimized_dnf(minimal_cover, parsed.variables)}",
        ]
    )
    sections["calculation_tabular"] = "\n".join(
        [
            render_gluing_stages(stages, parsed.variables),
            format_table(["Implicant", *[str(item) for item in ones]], chart) if chart else "No chart for constant 0.",
            f"Minimal DNF: {minimized_dnf(minimal_cover, parsed.variables)}",
        ]
    )
    sections["karnaugh"] = "\n".join(
        [
            render_kmaps(vector, parsed.variables, minimal_cover),
            f"Minimal DNF: {minimized_dnf(minimal_cover, parsed.variables)}",
        ]
    )
    return sections


def analyze_expression(expression: str) -> str:
    sections = build_analysis_sections(expression)
    titled_sections = [
        ("Summary", sections["summary"]),
        ("Truth table", sections["truth_table"]),
        ("Normal forms", sections["normal_forms"]),
        ("Numeric forms", sections["numeric_forms"]),
        ("Index form", sections["index_form"]),
        ("Post classes", sections["post_classes"]),
        ("Zhegalkin polynomial", sections["zhegalkin"]),
        ("Fictitious variables", sections["fictitious"]),
        ("Boolean derivatives", sections["derivatives"]),
        ("Calculation method", sections["calculation_method"]),
        ("Calculation-tabular method", sections["calculation_tabular"]),
        ("Karnaugh map", sections["karnaugh"]),
    ]
    return "\n\n".join(f"{title}:\n{content}" for title, content in titled_sections)
