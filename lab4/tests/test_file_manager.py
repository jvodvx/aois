import os

from hash_table import HashTable
from file_manager import (
    save_to_file,
    load_from_file
)


def test_save_and_load_file():

    filename = "test_data.txt"

    table = HashTable()

    table.insert(
        "Belgium",
        "Brussels"
    )

    table.insert(
        "France",
        "Paris"
    )

    save_to_file(
        filename,
        table
    )

    data = load_from_file(
        filename
    )

    assert (
        "Belgium",
        "Brussels"
    ) in data

    assert (
        "France",
        "Paris"
    ) in data

    os.remove(filename)


def test_load_non_existing_file():

    data = load_from_file(
        "missing_file.txt"
    )

    assert data == []