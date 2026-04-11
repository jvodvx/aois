from __future__ import annotations

from itertools import combinations
from typing import Sequence

from .minimization import build_kmap_tables, implicant_to_string
from .models import GluingStage, Implicant, TruthRow
from .properties import derivative_vector
from .truth_table import build_dnf_from_vector


def format_index_set(indices: Sequence[int]) -> str:
    return "(" + ", ".join(map(str, indices)) + ")"


def format_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    all_rows = [list(headers)] + [list(row) for row in rows]
    widths = [max(len(str(row[index])) for row in all_rows) for index in range(len(headers))]
    formatted = []
    for row_index, row in enumerate(all_rows):
        formatted.append(" | ".join(str(cell).ljust(widths[index]) for index, cell in enumerate(row)))
        if row_index == 0:
            formatted.append("-+-".join("-" * width for width in widths))
    return "\n".join(formatted)


def render_truth_table(rows: Sequence[TruthRow], variables: Sequence[str]) -> str:
    headers = ["i", *variables, "f"]
    table_rows = [
        [str(index), *[str(values[var]) for var in variables], str(result)]
        for index, (values, result) in enumerate(rows)
    ]
    return format_table(headers, table_rows)


def render_gluing_stages(stages: Sequence[GluingStage], variables: Sequence[str]) -> str:
    if not stages:
        return "Function is constant 0; no gluing is needed."

    lines = []
    for stage_index, stage in enumerate(stages, start=1):
        lines.append(f"Stage {stage_index}:")
        if stage.combinations:
            for item in stage.combinations:
                left = implicant_to_string(item.left, variables)
                right = implicant_to_string(item.right, variables)
                result = implicant_to_string(item.result, variables)
                left_ids = ",".join(map(str, sorted(item.left.minterms)))
                right_ids = ",".join(map(str, sorted(item.right.minterms)))
                result_ids = ",".join(map(str, sorted(item.result.minterms)))
                lines.append(f"  {left} [{left_ids}] + {right} [{right_ids}] -> {result} [{result_ids}]")
        else:
            lines.append("  No more combinations.")
        if stage.result:
            result_line = ", ".join(
                f"{implicant_to_string(implicant, variables)} [{','.join(map(str, sorted(implicant.minterms)))}]"
                for implicant in stage.result
            )
            lines.append(f"  Result: {result_line}")
        if stage.primes:
            prime_line = ", ".join(
                f"{implicant_to_string(implicant, variables)} [{','.join(map(str, sorted(implicant.minterms)))}]"
                for implicant in stage.primes
            )
            lines.append(f"  Prime implicants fixed on this stage: {prime_line}")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_derivatives(vector: Sequence[int], variables: Sequence[str]) -> str:
    if not variables:
        return "No variables."

    lines = []
    for order in range(1, min(4, len(variables)) + 1):
        for group in combinations(variables, order):
            remaining, derivative = derivative_vector(vector, variables, group)
            expression = build_dnf_from_vector(derivative, remaining)
            vector_string = "".join(map(str, derivative)) or "0"
            lines.append(
                f"d/d{''.join(group)}: vars={','.join(remaining) if remaining else '-'}; "
                f"vector={vector_string}; SDNF={expression}"
            )
    return "\n".join(lines)


def render_post_classes(classes: dict[str, bool]) -> str:
    return "\n".join(f"{name}: {'yes' if value else 'no'}" for name, value in classes.items())


def render_kmaps(vector: Sequence[int], variables: Sequence[str], cover: Sequence[Implicant]) -> str:
    if not variables:
        return f"Constant map: {vector[0]}"

    lines = []
    for table in build_kmap_tables(vector, variables):
        layer_prefix = ""
        if table.layer is not None:
            assignments = ",".join(f"{var}={bit}" for var, bit in zip(table.layers, table.layer))
            layer_prefix = f"[{assignments}] "
        row_label = "".join(table.row_vars) or "-"
        col_label = "".join(table.col_vars) or "-"
        headers = [f"{layer_prefix}{row_label}\\{col_label}", *table.col_labels]
        rows = [[row_name, *values] for row_name, values in table.rows]
        lines.append(format_table(headers, rows))
        lines.append("")

    if cover:
        lines.append("Selected groups:")
        for index, implicant in enumerate(cover, start=1):
            lines.append(f"  G{index}: {implicant_to_string(implicant, variables)} -> {sorted(implicant.minterms)}")
    return "\n".join(lines).rstrip()
