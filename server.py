import sys
import app
import os
import psycopg2

def create_user(details):
    name = str(details['firstname'])
    print(name)

    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO users (netid) "
                    + "VALUES (%s)",[name])


    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
    