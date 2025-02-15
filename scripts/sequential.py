import sys, io, pandas as pd, json, requests, re

# Ensure default encoding is set to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# **Functions to Format Each Product**
def format_description(product_description):
    """Decodes HTML entities, removes tags, and cleans text efficiently."""
    clean_text = re.sub(r"<[^>]*>", "", product_description).strip()

    return clean_text

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
def fetch_product(url):
    try:
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Referer": url,  # Sometimes helps
        "Accept": "application/json, text/plain, */*",
        "Connection": "keep-alive"
        }
        response = requests.get(url, headers=headers)  # Send GET request
        product = response.json()  # Convert text to JSON

        return format_product(product)  # Format and return product data
        
    except Exception as e:
        print(f"Error fetching {url}")
        return None  

# **Fetch All Products (Sequential)**
def fetch_all_products(url, products_ids, batch_size=1000):
    """Fetch products one by one while respecting rate limits."""
    results = []
    file_index = 189
    start_index = 185012  # Starting index for products

    for i in range(start_index, len(products_ids), batch_size):
        batch = products_ids[i:i + batch_size]

        for p_id in batch:
            product_url = url.format(p_id)
            fetched_product = fetch_product(product_url)
            results.append(fetched_product) if fetched_product else None

        # Save every batch_size products
        if len(results) >= batch_size:
            save_to_json(results, file_index, filename="data/batch_")
            results = []  # Reset batch
            file_index += 1

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
    batch_size = 1000
    
    # Load product IDs from the CSV file
    products_ids = pd.read_csv("data/products-0-200000(in).csv")["id"].tolist()
    
    # Define the API URL
    api_url = "https://api.tiki.vn/product-detail/api/v1/products/{}"

    # Fetch all products sequentially
    # fetch_all_products(api_url, products_ids, batch_size)

            


# **Run the Program**
if __name__ == "__main__":
    main()
