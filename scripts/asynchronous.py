from selenium import webdriver
from selenium.webdriver.common.by import By
import sys, io, pandas as pd, json, time, asyncio, aiohttp
from bs4 import BeautifulSoup


# Ensure default encoding is set to UTF-8
# The data contains special characters (Vietnamese) that are not supported by the default encoding 
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Functions to format each product returned by the API
def format_description(product_description):
    soup = BeautifulSoup(product_description, "html.parser")
    clean_text = soup.get_text(separator="\n", strip=True)
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

async def fetch_products(session, url, semaphore, delay=1):
    # Navigate to the API URL
    async with semaphore:
        await asyncio.sleep(delay)
        try:     
            async with session.get(url) as response:
                if response.status == 200:
                    product = await response.json()
                    formatted_product = format_product(product)
                    return formatted_product
                else:
                    print(f"Failed to fetch data from {url}. Status code: {response.status}")
                    return url
            
        except Exception as e:
            print("Error fetching data:", e)
            return url
    
async def fetch_all_products(url, products_ids, batch_size=1000, concurrency=50, delay=1):
    results = []
    failed_products = []
    file_index = 1

    semaphore = asyncio.Semaphore(concurrency)  # Limit the number of concurrent requests

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(products_ids), batch_size):
            batch = products_ids[i:i + batch_size]
            
            tasks = [fetch_products(session, url.format(p_id), semaphore, delay) for p_id in batch]
            fetched_products = await asyncio.gather(*tasks)

            successful_products = [product for product in fetched_products if isinstance(product, dict)]
            results.extend(successful_products)

            failed_urls = [product for product in fetched_products if product is isinstance(product, str)]
            failed_products.extend(failed_urls)

            print(f"Batch {file_index}: Fetched {len(successful_products)} products")

            # Save the results to a JSON file when the batch is full
            if len(results) == batch_size:
                save_to_json(results, file_index, filename="data/batch_")
                results = []    # Reset the batch
                file_index += 1
        
        # Save the remaining products
        if results:
            save_to_json(results, file_index, filename="data/batch_")
        # Save the failed products
        print(f"Fetching completed! Total failed products: {len(failed_products)}")
        if failed_products:
            save_to_json(failed_products, file_index=0, filename="data/failed_products_")

        

# Save Products in JSON Batches
def save_to_json(results, file_index, filename=None):
    filename = f"{filename}{file_index}.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)
    print(f"Saved {len(results)} products to {filename}")



def main():
    # driver = create_webdriver()
    
    # pipeline
    batch_size = 1000
    concurrency = 100
    delay = 10
    # Load products IDs from the CSV file
    products_ids = pd.read_csv("data\products-0-200000(in).csv")["id"].tolist()
    # Define the API URL
    api_url = "https://api.tiki.vn/product-detail/api/v1/products/{}"

    start_time = time.time()
    # Fetch all products
    asyncio.run(fetch_all_products(api_url, products_ids, batch_size, concurrency, delay))
        
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time: {total_time} seconds")

    # driver.quit()


if __name__ == "__main__":
    main()