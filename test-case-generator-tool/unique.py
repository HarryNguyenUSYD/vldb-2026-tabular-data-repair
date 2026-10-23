import csv
from pathlib import Path

csv_files = [
    "datasets/adult_20/clean.csv",
    "datasets/bank_marketing_222/clean.csv",
    "datasets/census_income_kdd_117/clean.csv",
    "datasets/support2_880/clean.csv",
]

for file_path in csv_files:
    print(f"\n=== {file_path} ===")

    with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        unique_values = {
            column: set()
            for column in reader.fieldnames
        }

        for row in reader:
            for column, value in row.items():
                unique_values[column].add(value)

    for column, values in unique_values.items():
        print(f"\n{column}:")
        # for value in sorted(values):
        #     print(f"  {value}")
        print(len(values))