from selenium import webdriver
from selenium.webdriver.common.by import By
import sys
import io
import pandas as pd
import json
from bs4 import BeautifulSoup
import time

# Ensure default encoding is set to UTF-8
# The data contains special characters (Vietnamese) that are not supported by the default encoding 
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load products IDs from the CSV file
products_ids = pd.read_csv("data\products-0-200000(in).csv")["id"].tolist()
# Define the API URL
api_url = "https://api.tiki.vn/product-detail/api/v1/products/{}"


# Set up the Chrome WebDriver
def create_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no UI)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

# Functions to format each product returned by the API
def format_description(product_description):
    soup = BeautifulSoup(product_description, "html.parser")
    clean_text = soup.get_text()
    return clean_text

def format_product(product):
    return {
        # Using get() to handle missing keys
        "id": product.get("id", "Unknown"),  
        "name": product.get("name", "Unknown Product"),
        "url_key": product.get("url_key", ""),
        "price": product.get("price", 0.0),
        "description": format_description(product.get("description", "")),
        "images_url": [image["base_url"] for image in product.get("images", [])]
    }

def fetch_products(driver, url):
    # Navigate to the API URL
    driver.get(url)
    try:
        # Extract API response 
        response = driver.find_element(By.TAG_NAME, "pre").text  # The API response is often rendered in a <pre> tag
        product = json.loads(response)
    
        if not isinstance(product, dict):  # Ensure valid product data
            print(f"⚠️ Warning: Invalid product format for URL {url}")
            return None
        
        if "id" not in product:  # Check if 'id' key exists
            print(f"⚠️ Warning: Missing 'id' key in product data for URL {url}")
            return None
        
        return product
        
    except Exception as e:
        print("Error fetching data:", e)
        return None
    
    

# Save Products in JSON Batches
def save_to_json(results, file_index, filename=None):
    filename = f"{filename}{file_index}.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)
    print(f"Saved {len(results)} products to {filename}")



def main():
    driver = create_webdriver()
    
    # pipeline
    batch_size = 1000
    results = []
    failed_products = []
    file_index = 1

    start_time = time.time()
    for i, p_id in enumerate(products_ids):
        fetched_product = fetch_products(driver, api_url.format(p_id))
        if fetched_product:
            formatted_product = format_product(fetched_product)
            results.append(formatted_product)
        else:
            print(f"Failed to fetch product with ID: {p_id}")
            failed_products.append(p_id)
            continue
        
        # When the batch is full, save the results to a JSON file with the current file index
        if len(results) == batch_size:
            save_to_json(results, file_index=file_index, filename="data\batch_")
            results = []    # Reset the batch
            file_index += 1

    if results:
        save_to_json(results, file_index=0)
        
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time: {total_time} seconds")

    driver.quit()


if __name__ == "__main__":
    main()