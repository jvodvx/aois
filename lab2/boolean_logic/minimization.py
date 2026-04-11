from __future__ import annotations

from typing import Iterable, Optional, Sequence

from .models import CombinationStep, GluingStage, Implicant, KMapTable


def implicant_to_string(implicant: Implicant, variables: Sequence[str]) -> str:
    parts = []
    for variable, bit in zip(variables, implicant.pattern):
        if bit is None:
            continue
        parts.append(variable if bit == 1 else f"!{variable}")
    if not parts:
        return "1"
    if len(parts) == 1:
        return parts[0]
    return "(" + "&".join(parts) + ")"


def initial_implicants(minterms: Sequence[int], variables_count: int) -> list[Implicant]:
    return [
        Implicant(tuple(int(bit) for bit in format(minterm, f"0{variables_count}b")), frozenset({minterm}))
        for minterm in minterms
    ]


def unique_patterns(implicants: Iterable[Implicant]) -> list[Implicant]:
    unique: dict[tuple[Optional[int], ...], Implicant] = {}
    for implicant in implicants:
        if implicant.pattern not in unique:
            unique[implicant.pattern] = implicant
            continue
        unique[implicant.pattern] = Implicant(
            implicant.pattern,
            unique[implicant.pattern].minterms | implicant.minterms,
        )
    return list(unique.values())


def quine_mccluskey_stages(minterms: Sequence[int], variables: Sequence[str]) -> tuple[list[GluingStage], list[Implicant]]:
    if not minterms:
        return [], []

    current = unique_patterns(initial_implicants(minterms, len(variables)))
    stages: list[GluingStage] = []
    prime_implicants: list[Implicant] = []

    while True:
        combinations_list: list[CombinationStep] = []
        used_indices: set[int] = set()
        next_implicants: list[Implicant] = []

        for first_index in range(len(current)):
            for second_index in range(first_index + 1, len(current)):
                first = current[first_index]
                second = current[second_index]
                if not first.can_combine(second):
                    continue
                used_indices.add(first_index)
                used_indices.add(second_index)
                combined = first.combine(second)
                next_implicants.append(combined)
                combinations_list.append(CombinationStep(first, second, combined))

        primes = [current[index] for index in range(len(current)) if index not in used_indices]
        prime_implicants.extend(primes)
        deduped_next = unique_patterns(next_implicants)
        stages.append(GluingStage(current, combinations_list, deduped_next, primes))

        if not deduped_next:
            break
        current = deduped_next

    return stages, unique_patterns(prime_implicants)


def select_minimal_cover(prime_implicants: Sequence[Implicant], minterms: Sequence[int], variables: Sequence[str]) -> list[Implicant]:
    if not minterms:
        return []

    variables_count = len(variables)
    cover_map: dict[int, list[int]] = {
        minterm: [
            index
            for index, implicant in enumerate(prime_implicants)
            if implicant.covers(minterm, variables_count)
        ]
        for minterm in minterms
    }

    selected: set[int] = set()
    covered: set[int] = set()

    for minterm, options in cover_map.items():
        if len(options) == 1:
            selected.add(options[0])

    for index in selected:
        for minterm in minterms:
            if prime_implicants[index].covers(minterm, variables_count):
                covered.add(minterm)

    remaining_minterms = [minterm for minterm in minterms if minterm not in covered]
    if not remaining_minterms:
        return [prime_implicants[index] for index in sorted(selected)]

    candidate_indices = sorted(
        {
            index
            for minterm in remaining_minterms
            for index in cover_map[minterm]
            if index not in selected
        }
    )
    best: Optional[tuple[int, int, tuple[int, ...]]] = None

    def search(chosen: tuple[int, ...], uncovered: tuple[int, ...]) -> None:
        nonlocal best
        if not uncovered:
            all_indices = tuple(sorted(set(chosen) | selected))
            literal_cost = sum(prime_implicants[index].literal_count() for index in all_indices)
            score = (len(all_indices), literal_cost, all_indices)
            if best is None or score < best:
                best = score
            return

        if best is not None and len(set(chosen) | selected) >= best[0]:
            return

        pivot = min(uncovered, key=lambda item: len([idx for idx in cover_map[item] if idx in candidate_indices]))
        options = [idx for idx in cover_map[pivot] if idx in candidate_indices]
        for option in options:
            next_uncovered = tuple(
                minterm
                for minterm in uncovered
                if not prime_implicants[option].covers(minterm, variables_count)
            )
            search(tuple(sorted(set(chosen) | {option})), next_uncovered)

    search(tuple(), tuple(remaining_minterms))

    if best is None:
        return [prime_implicants[index] for index in sorted(selected)]
    return [prime_implicants[index] for index in best[2]]


def cover_table(prime_implicants: Sequence[Implicant], minterms: Sequence[int], variables: Sequence[str]) -> list[list[str]]:
    variables_count = len(variables)
    table = []
    for implicant in prime_implicants:
        row = [implicant_to_string(implicant, variables)]
        for minterm in minterms:
            row.append("X" if implicant.covers(minterm, variables_count) else "")
        table.append(row)
    return table


def minimized_dnf(implicants: Sequence[Implicant], variables: Sequence[str]) -> str:
    if not implicants:
        return "0"
    return " | ".join(implicant_to_string(implicant, variables) for implicant in implicants)


def gray_codes(bits: int) -> list[str]:
    if bits == 0:
        return [""]
    if bits == 1:
        return ["0", "1"]
    previous = gray_codes(bits - 1)
    return ["0" + code for code in previous] + ["1" + code for code in reversed(previous)]


def kmap_layout(variables: Sequence[str]) -> tuple[list[str], list[str], list[str]]:
    count = len(variables)
    if count == 0:
        return [], [], []
    if count == 1:
        return [], [], [variables[0]]
    if count == 2:
        return [], [variables[0]], [variables[1]]
    if count == 3:
        return [], [variables[0]], list(variables[1:])
    if count == 4:
        return [], list(variables[:2]), list(variables[2:])
    return [variables[0]], list(variables[1:3]), list(variables[3:])


def build_kmap_tables(vector: Sequence[int], variables: Sequence[str]) -> list[KMapTable]:
    layers, row_vars, col_vars = kmap_layout(variables)
    layer_codes = gray_codes(len(layers))
    row_codes = gray_codes(len(row_vars))
    col_codes = gray_codes(len(col_vars))
    tables: list[KMapTable] = []

    for layer_code in layer_codes:
        layer_assignment = dict(zip(layers, [int(bit) for bit in layer_code]))
        rows: list[tuple[str, list[str]]] = []
        for row_code in row_codes:
            row_assignment = dict(zip(row_vars, [int(bit) for bit in row_code]))
            row_values = []
            for col_code in col_codes:
                col_assignment = dict(zip(col_vars, [int(bit) for bit in col_code]))
                values = {**layer_assignment, **row_assignment, **col_assignment}
                bits = "".join(str(values[var]) for var in variables)
                row_values.append(str(vector[int(bits, 2)]))
            rows.append((row_code or "-", row_values))
        tables.append(
            KMapTable(
                layer=layer_code or None,
                layers=layers,
                row_vars=row_vars,
                col_vars=col_vars,
                rows=rows,
                col_labels=[label or "-" for label in col_codes],
            )
        )
    return tables
