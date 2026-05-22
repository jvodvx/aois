def load_from_file(filename):

    data = []

    try:
        with open(filename, "r", encoding="utf-8") as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                key, value = line.split(":")

                data.append(
                    (key.strip(), value.strip())
                )

    except FileNotFoundError:
        print("File not found")

    return data


def save_to_file(filename, table):

    with open(filename, "w", encoding="utf-8") as file:

        for entry in table.table:

            if entry.occupied and not entry.deleted:

                file.write(
                    f"{entry.key}:{entry.value}\n"
                )

    print("Data saved")