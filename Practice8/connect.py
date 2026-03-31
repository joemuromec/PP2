import psycopg2
from config import params

def get_connection():
    try:
        with psycopg2.connect(**params) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
