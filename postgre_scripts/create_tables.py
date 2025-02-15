import psycopg2
from config import load_config

def create_tables(commands):
    try:
        config = load_config()
        with psycopg2.connect(**config) as connection:
            with connection.cursor() as cursor:
                cursor.execute(commands)
            connection.commit()
            print("Tables created successfully")
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
    

if __name__ == '__main__':
    commands = """
        CREATE TABLE tiki_products (
            id SERIAL PRIMARY KEY, 
            product_name VARCHAR(255) NOT NULL,
            url_key VARCHAR(255) NOT NULL,
            price INTEGER NOT NULL,
            description TEXT NOT NULL,
            images_url TEXT[]
            )
        """
    create_tables(commands)