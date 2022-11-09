import os
import sys
import psycopg2

#-----------------------------------------------------------------------

def main():
    DATABASE_URL = "postgres://metodtec:UXyLIu_ypLGXhYlbP5Px1unu1nPFhqgR@rajje.db.elephantsql.com/metodtec"

    if len(sys.argv) != 1:
        print('Usage: python create.py', file=sys.stderr)
        sys.exit(1)

    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                #-------------------------------------------------------

                cursor.execute("DROP TABLE IF EXISTS users")
                cursor.execute("CREATE TABLE users "
                    + "(netid TEXT, name TEXT, usertype TEXT, year TEXT, plan TEXT)")

                # #-------------------------------------------------------

                cursor.execute("DROP TABLE IF EXISTS contact")
                cursor.execute("CREATE TABLE contact "
                    + "(netid TEXT, phone TEXT, email TEXT)")

                # #-------------------------------------------------------

                cursor.execute("DROP TABLE IF EXISTS requested")
                cursor.execute("CREATE TABLE requested "
                    + "(reqid INT GENERATED ALWAYS AS IDENTITY, netid TEXT, requested TEXT, times TEXT)")

                #-------------------------------------------------------

                cursor.execute("DROP TABLE IF EXISTS exchanges")
                cursor.execute("CREATE TABLE exchanges "
                    + "(reqid INT, netid TEXT, swapnetid TEXT, times TEXT, completed TEXT)")
                
                #-------------------------------------------------------

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
