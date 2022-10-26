import sys
import app
import os
import psycopg2

DATABASE_URL = "postgres://metodtec:UXyLIu_ypLGXhYlbP5Px1unu1nPFhqgR@rajje.db.elephantsql.com/metodtec"


def create_user(details):
    netid = details['netid']
    year = details['year']
    plan = details['plan']
    print(netid)
    print(year)
    print(plan)

    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:

                cursor.execute("INSERT INTO users "
                    + "VALUES (netid, 'user', year, plan)")

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
    