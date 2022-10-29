import sys
import app
import os
import psycopg2

def create_user(details):
    netid = str(details['netid'])
    year = str(details['year'])
    plan = str(details['plan'])
    user = 'user'
    val = (netid, user, year, plan)

    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO users (netid, usertype, year, plan) "
                    + "VALUES (%s, %s, %s, %s)", val)


    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
    