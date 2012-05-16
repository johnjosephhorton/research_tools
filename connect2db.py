import psycopg2 
import settings 

def get_db_connection():
    """Creates a connection to the database""" 
    return psycopg2.connect(settings.DB_CONNECT_STRING)


