import sys
import app
import os
import psycopg2
import notifications

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

    usersOld, contactOld = profile_details(netid)

    netid = str(netid)
    name = str(usersOld[1])
    year = str(usersOld[3])
    plan = str(usersOld[4]) 
    phone = str(contactOld[1])

    if details['year'] != "":
        year = str(details['year'])

    if details['plan'] != "":
        plan = str(details['plan'])

    if details['name'] != "":
        name = str(details['name'])

    if details['number'] != "":
        phone = str(details['number'])
    

    # year = str(details['year'])
    # plan = str(details['plan'])
    # name = str(details['name'])
    users = (name, year, plan, netid)

    # phone = str(details['number'])
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
    requested_plan = details['plan']
    times = details['times']

    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:

                    cursor.execute("SELECT plan FROM users WHERE netid = %s",[username])
                    user_plan = cursor.fetchone()

                    # cursor.execute("SELECT netid FROM users WHERE plan = %s",[user_plan])
                    # netids = []
                    # netid = cursor.fetchone()
                    # while netid is not None:
                    #     netids.append(row)
                    #     netid = cursor.fetchone
                    # seperator = ', '
                    # stmt_str = seperator.join(netids)
                    
                    cursor.execute("SELECT * FROM requested WHERE requested = %s AND times = %s AND netid IN (SELECT netid FROM users WHERE plan = %s AND netid != %s)",[user_plan,times, requested_plan, username])
                    req = cursor.fetchone()

                    if req is None:
                        requested = (username, requested_plan, times)
                        print(requested)
                        cursor.execute("INSERT INTO requested (netid, requested, times) "
                        + "VALUES (%s, %s, %s)", requested)

# need to add notification
                    else:
                        print('exchange')
                        accept_request(req[0], username)


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
                
                cursor.execute("SELECT * FROM requested WHERE requested = %s AND netid NOT IN (SELECT block_id FROM blocked WHERE netid = %s) AND netid != %s",[plan, username, username])
                rows = cursor.fetchall()

                cursor.execute("SELECT reqid FROM deletedrequest WHERE netid = %s",[username])
                deleted = cursor.fetchall()
                
                
                if rows is not None:
                    for row in rows:
                        reqid = row[0]

                        flag = False
                        for delete in deleted:
                            if reqid == delete[0]:
                                flag = True

                        if flag == False:        
                            
                            netid = row[1]
                            requested_dining_plan = row[2]
                            times = row[3]
                            cursor.execute("SELECT plan FROM users WHERE netid = %s",[netid])
                            offer_dining_plan = cursor.fetchone()
                            request = [requested_dining_plan, offer_dining_plan[0], times, netid, reqid]
                    
                            requested.append(request)

                return requested    
            
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

def trash_requests(username):

    username = str(username)
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                requested = []

                cursor.execute("SELECT reqid FROM deletedrequest WHERE netid = %s",[username])
                deleted = cursor.fetchall()

                if deleted is not None:
                    for delete in deleted:

                        cursor.execute("SELECT * FROM requested WHERE reqid = %s",[delete[0]])
                        row = cursor.fetchone()

                        if row is not None:
                            netid = row[1]
                            requested_dining_plan = row[2]
                            times = row[3]
                            cursor.execute("SELECT plan FROM users WHERE netid = %s",[netid])
                            offer_dining_plan = cursor.fetchone()
                            request = [requested_dining_plan, offer_dining_plan[0], times, netid, delete[0]]
                    
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
                        reqid = row[0]
                        netid = row[1]
                        requested_dining_plan = row[2]
                        times = row[3]
                        cursor.execute(
                            "SELECT plan FROM users WHERE netid = %s", [netid])
                        offer_dining_plan = cursor.fetchone()
                        request = [requested_dining_plan, times, netid, reqid]

                        requested.append(request)

                return requested
            
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
            
def get_request(id):
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                requested = []
                print("ID")
                print(id)
                cursor.execute(
                    "SELECT * FROM requested WHERE reqid = %s", [id])
                req = cursor.fetchone()

        
                return req

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
        

def get_exchange(id):
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                requested = []
                print("ID")
                print(id)
                cursor.execute(
                    "SELECT * FROM exchanges WHERE reqid = %s", [id])
                req = cursor.fetchone()

        
                return req

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

def get_request(id):
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                requested = []
                print("ID")
                print(id)
                cursor.execute(
                    "SELECT * FROM requested WHERE reqid = %s", [id])
                req = cursor.fetchone()

        
                return req

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


def accept_request(id, username):
    print("accepting request")
    
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                requested = []
                print("ID")
                print(id)
                cursor.execute(
                    "SELECT * FROM requested WHERE reqid = %s", [id])
                req = cursor.fetchone()
                print("REQ")
                print(req)
                print(username)
                
                info = (id, username, req[1], req[3], "FALSE")
                print("INFO")
                print(info)

                # notifications.send_message(num1, create_message(name1, name2))
                # notifications.send_message(num2, create_message(name2, name1))


                
                cursor.execute("INSERT INTO exchanges (reqid, netid, swapnetid, times, completed) "
                               + "VALUES (%s, %s, %s, %s, %s)", info)
                
                cursor.execute(
                    "DELETE FROM requested WHERE reqid = %s", [id])

                print('1')

                cursor.execute("SELECT phone FROM contact WHERE netid = %s", [username])
                num1 = cursor.fetchone()

                print('2')

                cursor.execute("SELECT phone FROM contact WHERE netid = %s", [req[1]])
                num2 = cursor.fetchone()

                print('3')

                cursor.execute("SELECT name FROM users WHERE netid = %s", [username])
                name1 = cursor.fetchone()

                print('4')

                cursor.execute("SELECT name FROM users WHERE netid = %s", [req[1]])
                name2 = cursor.fetchone()

                print(req[3])

                print(num1[0])
                print(num2[0])


                # msg = 'Hello, ' + str(name1[0]) + '! Great news, you have been matched with ' + str(name2[0]) + ' for ' + str(req[3])
                # msg += '. Please visit https://mealswap.onrender.com/exchanges to view more details about your exchange.'

                def create_message(name1, name2):
                    msg = 'Hello, ' + name1 + '! Great news, you have been matched with ' + name2 + ' for ' + req[3]
                    msg += '. Please visit https://mealswap.onrender.com/exchanges to view more details about your exchange.'
                    return msg
                
                notifications.send_message(num1[0], create_message(name1[0], name2[0]))
                notifications.send_message(num2[0], create_message(name2[0], name1[0]))



    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


def delete_request(id, username):
    print("deleting request")
    
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                requested = []
                print("ID")
                print(id)
                # cursor.execute(
                #     "SELECT * FROM requested WHERE reqid = %s", [id])
                # req = cursor.fetchone()
                print("REQ")
                # print(req)
                print(username)
                
                info = (id, username)
                print("INFO")
                print(info)
                
                cursor.execute("INSERT INTO deletedrequest (reqid, netid) "
                               + "VALUES (%s, %s)", info)
                
                # cursor.execute(
                #     "DELETE FROM requested WHERE reqid = %s", [id])

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


def cancel_exchange(id):
    print("cancelling exchange")
    
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM exchanges WHERE reqid = %s", [id])

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


def cancel_request(id):
    print("cancelling exchange")
    
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM requested WHERE reqid = %s", [id])

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

def undo_request(id, username):
    
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM deletedrequest WHERE reqid = %s AND netid = %s", [id, username])

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

def block_user(reqid, username):
    
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                print(reqid)
                cursor.execute("SELECT * FROM exchanges WHERE reqid = %s", [reqid])

                exchange = cursor.fetchone()
                print(exchange)

                netid = exchange[1]
                if netid == username:
                    netid = exchange[2]

                cursor.execute("INSERT INTO blocked (netid, block_id) "
                    + "VALUES (%s, %s)", [username, netid])

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)



def get_exchanges(username):
    username = str(username)
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                requested = []

                cursor.execute(
                    "SELECT * FROM exchanges WHERE (netid = %s OR swapnetid = %s) AND netid NOT IN (SELECT block_id FROM blocked WHERE netid = %s) AND swapnetid NOT IN (SELECT block_id FROM blocked WHERE netid = %s)", [username, username, username, username])

                rows = cursor.fetchall()
                print(rows)

                if rows is not None:
                    for row in rows:
                        exchange_id = row[0]
                        netid = row[1]
                        swapnetid = row[2]
                        times = row[3]
                        completed = row[4]
                        if swapnetid == username:
                            swapnetid = netid
                        cursor.execute(
                            "SELECT * FROM users WHERE netid = %s", [swapnetid])
                        user = cursor.fetchone()
                        name = user[1]
                        year = user[3]
                        plan = user[4]
                        cursor.execute(
                            "SELECT * FROM contact WHERE netid = %s",[swapnetid])
                        contact = cursor.fetchone()
                        phone = contact[1]
                        email = contact[2]
                        request = [exchange_id, swapnetid, name, year, plan, phone, email, times, completed]
                        print(request)
                        requested.append(request)

                return requested

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
        