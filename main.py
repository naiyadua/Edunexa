import csv

print("1. View Institutions")
print("2. Add Institution")

choice = input("Enter choice: ")

if choice == "1":

    city = input("Enter city: ")

    with open("data.csv", "r") as file:
        reader = csv.DictReader(file)

        found = False

        for row in reader:
            if row["city"].lower() == city.lower():
                print(row["name"], "-", row["type"])
                found = True

        if not found:
            print("No institutions found.")

elif choice == "2":

    name = input("Institution Name: ")
    city = input("City: ")
    inst_type = input("Type (School/College): ")

    with open("data.csv", "a") as file:
        file.write(f"\n{name},{city},{inst_type}")

    print("Institution Added Successfully!")