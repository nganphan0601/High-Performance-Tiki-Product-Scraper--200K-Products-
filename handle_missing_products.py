import json
import os
import csv
import pandas as pd

# Directory where JSON files are stored
json_dir = "data"  # Change this to your actual directory

# Set to store fetched product IDs
fetched_product_ids = set()

# Loop through each JSON file and extract product IDs
for filename in os.listdir(json_dir):
    if filename.endswith(".json"):
        file_path = os.path.join(json_dir, filename)

        with open(file_path, "r", encoding="utf-8") as file:
            products = json.load(file)  # Load JSON content
            for product in products:
                fetched_product_ids.add(product["id"])  # Store product ID

print(f"Total fetched products: {len(fetched_product_ids)}")

# Path to CSV file containing expected product IDs
csv_file_path = "data\products-0-200000(in).csv"  # Change this to your actual file path

# Set to store expected product IDs
expected_product_ids = set()

# Read product IDs from CSV
products_id = pd.read_csv(csv_file_path)["id"].tolist()
for product_id in products_id:
    expected_product_ids.add(str(product_id))

print(f"Total expected product IDs: {len(expected_product_ids)}")


# Find the missing product IDs
missing_product_ids = expected_product_ids - fetched_product_ids

print(f"Total missing products: {len(missing_product_ids)}")

# Save missing IDs to retry later
# with open("data\missing_product_ids.json", "w", encoding="utf-8") as file:
#     json.dump(list(missing_product_ids), file, indent=4)

# print("Missing product IDs saved to 'missing_product_ids.json'")
