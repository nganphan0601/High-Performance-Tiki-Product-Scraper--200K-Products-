import requests
import json
import sys
import io


# Ensure default encoding is set to UTF-8
# The data contains special characters (Vietnamese) that are not supported by the default encoding 
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Components of the API call
productId = 138083218
base_url = f"https://api.tiki.vn/product-detail/api/v1/products/{productId}"

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    
}
# Function to get data from the API
def get_data(url, headers):
    response = requests.get(url, headers)
    if response.status_code == 200:
        response = response.json()
        print(response)
    else:
        print(f"Error {response.status_code}: {response.text}")

# Get the ids of the products from the csv file



test = {}
test['data'] = get_data(base_url, headers)
print(f"Data: {test['data']}")


