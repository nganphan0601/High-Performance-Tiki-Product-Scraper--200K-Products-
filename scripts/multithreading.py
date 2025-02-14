import sys, io, pandas as pd, json, time, requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import threading


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
def fetch_product(url, delay, results_list):
    """Fetch product details from the API using Selenium while handling rate limits."""
    time.sleep(delay)  # Respect API rate limits
    driver = create_webdriver()

    try:
        driver.get(url)
        response_text = driver.find_element(By.TAG_NAME, "pre").text  # Extract JSON response
        product = json.loads(response_text)  # Convert text to JSON
        results_list.append(format_product(product))  # Format and return product data        
    
    except Exception as e:
        print(f"Error fetching {url} using Selenium: {e}")
        return None  
    finally:
        driver.quit()

# **Fetch All Products (Sequential)**
def fetch_all_products(url, products_ids, batch_size=1000, delay=0.1, max_threads=5):
    """Fetch products one by one while respecting rate limits."""
    results = []
    file_index = 67 # Starting file index for saving batches
    start_index = 66003  # Starting index for products
    threads = []

    for p_id in products_ids[start_index:]: 
        product_url = url.format(p_id)

        # Create a thread for each product fetch
        thread = threading.Thread(target=fetch_product, args=(product_url, delay, results))
        threads.append(thread)
        thread.start()

        # Limit the number of active threads
        if len(threads) >= max_threads:
            for t in threads:
                t.join()  # Wait for threads to complete
            threads = []  # Reset thread list after each batch

        # Save batch to JSON
        if len(results) >= batch_size:
            save_to_json(results, file_index, filename="data/batch_")
            results = []
            file_index += 1

    # Wait for remaining threads to finish
    for t in threads:
        t.join()

    # Save remaining products
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
    # driver = create_webdriver()
    batch_size = 1000
    delay = 0.2  # Adjust based on API limits (set lower if possible)
    max_threads = 5

    # Load product IDs from the CSV file
    products_ids = pd.read_csv("data/products-0-200000(in).csv")["id"].tolist()
    
    # Define the API URL
    api_url = "https://api.tiki.vn/product-detail/api/v1/products/{}"

    start_time = time.time()

    # Fetch all products sequentially
    fetch_all_products(api_url, products_ids, batch_size, delay, max_threads)

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time: {total_time:.2f} seconds")

    # driver.quit()

# **Run the Program**
if __name__ == "__main__":
    main()
