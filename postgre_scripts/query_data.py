import psycopg2
from config import load_config

def query_data():
    config = load_config()
    try: 
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, product_name, url_key, price FROM tiki_products LIMIT 10")
                row=cur.fetchone()

                while row is not None:
                    print(row)
                    row=cur.fetchone()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

if __name__ == '__main__':
    query_data()