import sys
import app
import os
import psycopg2

def create_user(details, netid):
    netid = str(netid)
    year = str(details['year'])
    plan = str(details['plan'])
    user = 'user'
    name = str(details['name'])
    users = (netid, name, user, year, plan)
    phone = str(details['number'])
    email = netid + "@princeton.edu"
    contact = (netid, phone, email)

    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO users (netid, name, usertype, year, plan) "
                    + "VALUES (%s, %s, %s, %s, %s)", users)
    
                cursor.execute("INSERT INTO contact (netid, phone, email) "
                    + "VALUES (%s, %s, %s)", contact)
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

def check_user(username):

    username = str(username)
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE netid = %s",[username])
                row = cursor.fetchone()
                if row is None:
                    return -1
                else:
                    return 0

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

def profile_details(username):

    username = str(username)
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE netid = %s",[username])
                row = cursor.fetchone()
                cursor.execute("SELECT * FROM contact WHERE netid = %s",[username])
                row2 = cursor.fetchone()
                return (row, row2)     

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
    