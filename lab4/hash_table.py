from hash_entry import HashEntry
from utils import calculate_v, hash_function
from constants import TABLE_SIZE


class HashTable:

    def __init__(self):

        self.table = [
            HashEntry()
            for _ in range(TABLE_SIZE)
        ]

        self.count = 0

    def insert(self, key, value):

        if self.search(key) is not None:
            print("Duplicate key")
            return

        v = calculate_v(key)
        index = hash_function(v)

        print(f"\nINSERT: {key}")
        print(f"V = {v}")
        print(f"h(V) = {index}")

        original_index = index
        step = 0

        collision_occurred = False

        while (
            self.table[index].occupied
            and not self.table[index].deleted
        ):

            collision_occurred = True

            print(f"Collision at index {index}")

            self.table[index].collision = True

            previous_index = index

            step += 1

            index = (
                original_index + step
            ) % TABLE_SIZE

            self.table[previous_index].p0 = index
            self.table[previous_index].terminal = False

            print(f"Trying index {index}")

        entry = HashEntry(
            key=key,
            value=value,
            collision=collision_occurred,
            occupied=True,
            terminal=True,
            link=False,
            deleted=False,
            p0=-1
        )

        self.table[index] = entry

        self.count += 1

        print(f"Inserted at index {index}\n")

    def search(self, key):

        v = calculate_v(key)
        index = hash_function(v)

        original_index = index
        step = 0

        while self.table[index].occupied:

            print(f"Checking index {index}")

            entry = self.table[index]

            if (
                not entry.deleted
                and entry.key == key
            ):
                return entry.value

            step += 1

            if step >= TABLE_SIZE:
                break

            index = (
                original_index + step
            ) % TABLE_SIZE

        return None

    def delete(self, key):

        v = calculate_v(key)
        index = hash_function(v)

        original_index = index
        step = 0

        while self.table[index].occupied:

            entry = self.table[index]

            if (
                not entry.deleted
                and entry.key == key
            ):

                entry.deleted = True

                self.count -= 1

                print(f"{key} deleted")

                return

            step += 1

            if step >= TABLE_SIZE:
                break

            index = (
                original_index + step
            ) % TABLE_SIZE

        print(f"{key} not found")

    def display(self):

        print(
            "\n================ HASH TABLE ================\n"
        )

        print(
            f"{'Idx':<5}"
            f"{'ID':<15}"
            f"{'C':<5}"
            f"{'U':<5}"
            f"{'T':<5}"
            f"{'L':<5}"
            f"{'D':<5}"
            f"{'P0':<5}"
            f"{'Pi(DATA)':<15}"
        )

        print("-" * 70)

        for index, entry in enumerate(self.table):

            if entry.occupied:

                print(
                    f"{index:<5}"
                    f"{str(entry.key):<15}"
                    f"{str(int(entry.collision)):<5}"
                    f"{str(int(entry.occupied)):<5}"
                    f"{str(int(entry.terminal)):<5}"
                    f"{str(int(entry.link)):<5}"
                    f"{str(int(entry.deleted)):<5}"
                    f"{str(entry.p0):<5}"
                    f"{str(entry.value):<15}"
                )

            else:

                print(
                    f"{index:<5}"
                    f"{'-':<15}"
                    f"{'-':<5}"
                    f"{'0':<5}"
                    f"{'-':<5}"
                    f"{'-':<5}"
                    f"{'-':<5}"
                    f"{'-':<5}"
                    f"{'-':<15}"
                )

        print(
            "\n============================================\n"
        )

    def load_factor(self):

        return round(
            self.count / TABLE_SIZE,
            2
        )