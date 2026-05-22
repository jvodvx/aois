from hash_entry import HashEntry


def test_hash_entry_creation():

    entry = HashEntry(
        key="Belgium",
        value="Brussels",
        occupied=True
    )

    assert entry.key == "Belgium"
    assert entry.value == "Brussels"

    assert entry.occupied is True
    assert entry.deleted is False


def test_hash_entry_default_values():

    entry = HashEntry()

    assert entry.key is None
    assert entry.value is None

    assert entry.occupied is False
    assert entry.deleted is False