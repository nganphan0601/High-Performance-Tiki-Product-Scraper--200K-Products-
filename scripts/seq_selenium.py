import sys, io, pandas as pd, json, time, requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

# Ensure default encoding is set to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def create_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

# **Functions to Format Each Product**
def format_description(product_description):
    """Clean HTML tags from product descriptions."""
    soup = BeautifulSoup(product_description, "html.parser")
    return soup.get_text(separator="\n", strip=True)

def format_product(product):
    """Format product data and handle missing keys."""
    return {
        "id": product.get("id", "Unknown"),  
        "name": product.get("name", "Unknown Product"),
        "url_key": product.get("url_key", ""),
        "price": product.get("price", 0.0),
        "description": format_description(product.get("description", "")),
        "images_url": [image["base_url"] for image in product.get("images", [])]
    }

# **Fetch a Single Product (Synchronous)**
def fetch_product(driver, url):
    """Fetch product details from the API using Selenium while handling rate limits."""
    # time.sleep(delay)  # Respect API rate limits
    try:
        driver.get(url)
        response_text = driver.find_element(By.TAG_NAME, "pre").text  # Extract JSON response
        product = json.loads(response_text)  # Convert text to JSON

        return format_product(product)  # Format and return product data
        
    except Exception as e:
        print(f"Error fetching {url} using Selenium: {e}")
        return None  

# **Fetch All Products (Sequential)**
def fetch_all_products(driver, url, products_ids, batch_size=1000):
    """Fetch products one by one while respecting rate limits."""
    results = []
    file_index = 84
    start_index = 83008   # Starting index for products

    for i in range(start_index, len(products_ids), batch_size):
        batch = products_ids[i:i + batch_size]

        for p_id in batch:
            product_url = url.format(p_id)
            fetched_product = fetch_product(driver, product_url)
            results.append(fetched_product) if fetched_product else None

        # Save every batch_size products
        if len(results) >= batch_size:
            save_to_json(results, file_index, filename="data/batch_")
            results = []  # Reset batch
            file_index += 1

        # restart the driver to prevent memory leaks
        if i % 5000 == 0:
            driver.quit()
            driver = create_webdriver()

    # **Final Save for Remaining Products**
    if results:
        save_to_json(results, file_index, filename="data/batch_")

# **Save Products in JSON Batches**
def save_to_json(results, file_index, filename=None):
    """Save results to a JSON file."""
    if not results:
        return
    full_filename = f"{filename}{file_index}.json"
    with open(full_filename, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)


# **Main Function**
def main():
    driver = create_webdriver()
    batch_size = 1000
    
    # Load product IDs from the CSV file
    products_ids = pd.read_csv("data/products-0-200000(in).csv")["id"].tolist()
    
    # Define the API URL
    api_url = "https://api.tiki.vn/product-detail/api/v1/products/{}"

    # Fetch all products sequentially
    fetch_all_products(driver, api_url, products_ids, batch_size)

    driver.quit()

# **Run the Program**
if __name__ == "__main__":
    main()
