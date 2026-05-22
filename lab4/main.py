from hash_table import HashTable
from file_manager import (
    load_from_file,
    save_to_file
)


def print_menu():

    print("\n========== MENU ==========")

    print("1. Insert")
    print("2. Search")
    print("3. Delete")
    print("4. Display table")
    print("5. Load from file")
    print("6. Save to file")
    print("7. Load factor")
    print("0. Exit")


def main():

    hash_table = HashTable()

    while True:

        print_menu()

        choice = input(
            "\nChoose option: "
        )

        if choice == "1":

            key = input("Enter key: ")
            value = input("Enter value: ")

            hash_table.insert(
                key,
                value
            )

        elif choice == "2":

            key = input(
                "Enter key to search: "
            )

            result = hash_table.search(key)

            if result is not None:
                print(f"Found: {result}")
            else:
                print("Not found")

        elif choice == "3":

            key = input(
                "Enter key to delete: "
            )

            hash_table.delete(key)

        elif choice == "4":

            hash_table.display()

        elif choice == "5":

            filename = input(
                "Enter filename: "
            )

            data = load_from_file(
                filename
            )

            for key, value in data:

                hash_table.insert(
                    key,
                    value
                )

        elif choice == "6":

            filename = input(
                "Enter filename: "
            )

            save_to_file(
                filename,
                hash_table
            )

        elif choice == "7":

            print(
                f"Load factor: "
                f"{hash_table.load_factor()}"
            )

        elif choice == "0":

            print("Program terminated")
            break

        else:

            print("Invalid option")


if __name__ == "__main__":
    main()