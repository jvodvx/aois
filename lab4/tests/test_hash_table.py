from hash_table import HashTable


def test_insert():

    table = HashTable()

    table.insert(
        "Belgium",
        "Brussels"
    )

    result = table.search(
        "Belgium"
    )

    assert result == "Brussels"


def test_collision_handling():

    table = HashTable()

    table.insert(
        "Belgium",
        "Brussels"
    )

    table.insert(
        "Belarus",
        "Minsk"
    )

    # Belgium -> 10
    # Belarus -> 11

    assert table.table[10].key == "Belgium"
    assert table.table[11].key == "Belarus"


def test_multiple_collisions():

    table = HashTable()

    table.insert(
        "Belgium",
        "Brussels"
    )

    table.insert(
        "Belarus",
        "Minsk"
    )

    table.insert(
        "Bebeb",
        "Beb"
    )

    assert table.table[10].key == "Belgium"
    assert table.table[11].key == "Belarus"
    assert table.table[12].key == "Bebeb"


def test_search_existing():

    table = HashTable()

    table.insert(
        "China",
        "Beijing"
    )

    result = table.search(
        "China"
    )

    assert result == "Beijing"


def test_search_non_existing():

    table = HashTable()

    result = table.search(
        "Unknown"
    )

    assert result is None


def test_delete():

    table = HashTable()

    table.insert(
        "France",
        "Paris"
    )

    table.delete(
        "France"
    )

    result = table.search(
        "France"
    )

    assert result is None


def test_deleted_flag():

    table = HashTable()

    table.insert(
        "France",
        "Paris"
    )

    table.delete(
        "France"
    )

    # France -> 7

    assert table.table[7].deleted is True


def test_duplicate_key():

    table = HashTable()

    table.insert(
        "Canada",
        "Ottawa"
    )

    table.insert(
        "Canada",
        "Duplicate"
    )

    assert table.count == 1


def test_load_factor():

    table = HashTable()

    table.insert(
        "Belgium",
        "Brussels"
    )

    table.insert(
        "France",
        "Paris"
    )

    assert table.load_factor() == 0.1


def test_terminal_flags():

    table = HashTable()

    table.insert(
        "Belgium",
        "Brussels"
    )

    table.insert(
        "Belarus",
        "Minsk"
    )

    assert table.table[10].terminal is False
    assert table.table[11].terminal is True


def test_p0_links():

    table = HashTable()

    table.insert(
        "Belgium",
        "Brussels"
    )

    table.insert(
        "Belarus",
        "Minsk"
    )

    assert table.table[10].p0 == 11