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



def update_details(details, netid):
    netid = str(netid)
    year = str(details['year'])
    plan = str(details['plan'])
    name = str(details['name'])
    users = (name, year, plan, netid)

    phone = str(details['number'])
    contact = (phone, netid)

    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                cursor.execute("UPDATE users SET name=%s, year=%s, plan=%s WHERE netid=%s", users)
                cursor.execute("UPDATE contact SET phone=%s WHERE netid=%s", contact)

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

def create_request(details, username):

    username = str(username)
    plan = details['plan']
    times = details['times']
    requested = (username, plan, times)

    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO requested (netid, requested, times) "
                    + "VALUES (%s, %s, %s)", requested)

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

def get_requests(username):

    username = str(username)
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                requested = []

                cursor.execute("SELECT plan FROM users WHERE netid = %s",[username])
                plan = cursor.fetchone()
                print(plan)
                cursor.execute("SELECT * FROM requested WHERE requested = %s AND netid != %s",[plan, username])
                rows = cursor.fetchall()
                
                if rows is not None:
                    for row in rows:
                        netid = row[0]
                        requested_dining_plan = row[1]
                        times = row[2]
                        cursor.execute("SELECT plan FROM users WHERE netid = %s",[netid])
                        offer_dining_plan = cursor.fetchone()
                        request = [requested_dining_plan, offer_dining_plan[0], times, netid]
                
                        requested.append(request)

                return requested    

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


def get_your_requests(username):
    username = str(username)
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                requested = []

                cursor.execute(
                    "SELECT * FROM requested WHERE netid = %s", [username])
                rows = cursor.fetchall()

                if rows is not None:
                    for row in rows:
                        netid = row[0]
                        requested_dining_plan = row[1]
                        times = row[2]
                        cursor.execute(
                            "SELECT plan FROM users WHERE netid = %s", [netid])
                        offer_dining_plan = cursor.fetchone()
                        request = [requested_dining_plan, times, netid]

                        requested.append(request)

                return requested

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
