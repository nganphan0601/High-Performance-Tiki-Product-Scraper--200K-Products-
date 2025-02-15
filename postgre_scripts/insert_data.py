import psycopg2, json
from config import load_config

def insert_data(commands, product_list):
    config = load_config()
    try:
        with psycopg2.connect(**config) as connection:
            with connection.cursor() as cursor:
                cursor.executemany(commands, product_list)
            connection.commit()
            print("Data inserted successfully")
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


if __name__ == '__main__':
    table = "tiki_products"
    commands = (
        """
        INSERT INTO {} (id, product_name, url_key, price, description, images_url)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """)
    
    # Transform the data from json files to a list of tuples
    list_of_products = []
    for i in range(1, 189):
        with open(f"../data/batch_{i}.json", "r", encoding="utf-8") as file:
            products = json.load(file)
            for product in products:
                if product["id"] != "Unknown":
                    list_of_products.append((product["id"], product["name"], product["url_key"], product["price"], product["description"], product["images_url"]))
    insert_data(commands.format(table), list_of_products)

