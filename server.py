import sys
import app
import os
import psycopg2
import notifications
import req_lib


numbers = {'6506958443', '2485332973', '2489466588', '2019522343', '3124592594', '7035019474', '6092582211', '2672261984'}

def create_user(details, netid):
    netid = str(netid)
    # year = str(details['year'])
    plan = str(details['plan'])
    nickname = str(details['name'])
    phone = str(details['number'])
    lib = req_lib.ReqLib()

    req = lib.getJSON(
        lib.configs.USERS_BASIC,
        uid=netid,
    )

    name = req[0]['displayname']
    users = (netid, name, nickname, plan, phone)

    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO users (netid, name, nickname, plan, phone) "
                    + "VALUES (%s, %s, %s, %s, %s)", users)
    
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

def get_blocked(username):
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM blocked WHERE netid = %s", [username])
                rows = cursor.fetchall()
                table = []

                if rows is not None:
                    for row in rows:
                        # cursor.execute("SELECT * FROM users WHERE netid = %s", [row[2]])
                        # name = cursor.fetchone()
                        # row = [0, 0, 0, 0]
                        print(row)
                        lib = req_lib.ReqLib()

                        req = lib.getJSON(
                            lib.configs.USERS_BASIC,
                            uid=row[2],
                        )
                        name = ['', '', '']
                        
                        if len(req) != 0:
                            print(req[0]['displayname'])
                        
                        name = [0, 0, 0, 0]
                        table.append(
                            [row[0], row[2], req[0]['displayname'], name[2]])
            return table
        
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


def update_details(details, netid):

    usersOld = profile_details(netid)

    netid = str(netid)
    nickname = str(usersOld[2])
    plan = str(usersOld[3]) 
    phone = str(usersOld[4])

    if details['plan'] != "":
        plan = str(details['plan'])

    if details['name'] != "":
        name = str(details['name'])

    if details['number'] != "":
        phone = str(details['number'])
    

    # year = str(details['year'])
    # plan = str(details['plan'])
    # name = str(details['name'])
    users = (name, plan, phone, netid)

    # phone = str(details['number'])

    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                cursor.execute("UPDATE users SET nickname=%s, plan=%s, phone=%s WHERE netid=%s", users)
        
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

def check_for_instant_matches(username):
    
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                matches = "SELECT p1, p2, p1_reqid, p2_reqid "
                matches += "FROM(SELECT req1.netid as p1, req2.netid as p2,"
                matches += "req1.reqid as p1_reqid, req2.reqid as p2_reqid, "
                matches += "req1.requested as p1_req, req2.requested as p2_req, "
                matches += "req1.plan as p1_plan, req2.plan as p2_plan "
                matches += "FROM(SELECT reqid, users.netid, requested, times, plan FROM requested, users WHERE requested.netid=users.netid) req1 "
                matches +=    "JOIN(SELECT reqid, users.netid, requested, times, plan FROM requested, users WHERE requested.netid=users.netid) req2 "
                matches +=    "ON req1.netid=%s AND req2.netid != %s AND req1.times=req2.times) reqs "
                matches += "WHERE p1_req = p2_plan AND p2_req = p1_plan "
                matches += "AND p2 NOT IN(SELECT block_netid as netid FROM blocked WHERE netid=p1) "
                matches += "AND p1 NOT IN(SELECT block_netid as netid FROM blocked WHERE netid=p2) "
                matches += "AND p1_reqid NOT IN(SELECT reqid as p1_reqid FROM deletedrequest WHERE netid=p2) "
                matches +=  "AND p2_reqid NOT IN(SELECT reqid as p2_reqid FROM deletedrequest WHERE netid=p1) "

                cursor.execute(matches, [
                    username, username])

                reqs = cursor.fetchall()
                
                for req in reqs:
                    print(req)
                    
                    p1_username = req[1]
                    p2_username = req[0]
                    p1_reqid = req[3]
                    p2_reqid = req[2]
                    
                    if p1_username != username:
                        p1_username = req[0]
                        p2_username = req[1]
                        p1_reqid = req[2]
                        p2_reqid = req[3]
                    # delete second request
                    print(f'your username: {p1_username}')
                    cursor.execute("DELETE FROM requested WHERE reqid=%s", [p1_reqid])
                    
                    # accept first request
                    accept_request(p2_reqid, p1_username)
                    return True
                
                return False
            
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
                    
                    statement = "SELECT * FROM requested "
                    statement += "WHERE requested = %s AND times = %s AND netid IN (SELECT netid FROM users WHERE plan = %s AND netid != %s) "
                    statement += "AND netid NOT IN (SELECT block_netid as netid FROM blocked WHERE netid= %s) " 
                    statement += "AND reqid NOT IN (SELECT requested.reqid as reqid FROM requested, deletedrequest WHERE deletedrequest.reqid=requested.reqid AND deletedrequest.netid=%s AND requested =%s AND times =%s)"
                    
                    cursor.execute(statement,[user_plan,times, requested_plan, username, username, username, user_plan, times])
                    
                    # 
                    
                    req = cursor.fetchone()
                    print(f'')

                    if req is None:
                        requested = (username, requested_plan, times)
                        print(requested)
                        cursor.execute("INSERT INTO requested (netid, requested, times) "
                        + "VALUES (%s, %s, %s)", requested)

# need to add notification
                    else:
                        print('exchange')
                        accept_request(req[0], username)
                        return True # returns true when instant match

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
                return (row)     

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
                
                cursor.execute("SELECT * FROM requested WHERE requested = %s AND netid NOT IN (SELECT block_netid FROM blocked WHERE netid = %s) AND netid != %s",[plan, username, username])
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
    print('in here')
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

                cursor.execute("SELECT phone FROM users WHERE netid = %s", [username])
                num1 = cursor.fetchone()

                print('2')

                cursor.execute("SELECT phone FROM users WHERE netid = %s", [req[1]])
                num2 = cursor.fetchone()

                print('3')

                cursor.execute("SELECT name FROM users WHERE netid = %s", [username])
                name1 = cursor.fetchone()
                cursor.execute("SELECT plan FROM users WHERE netid = %s", [username])
                place1 = cursor.fetchone()



                print('4')

                cursor.execute("SELECT name FROM users WHERE netid = %s", [req[1]])
                name2 = cursor.fetchone()
                cursor.execute("SELECT plan FROM users WHERE netid = %s", [req[1]])
                place2 = cursor.fetchone()

                print(req[3])

                print(num1[0])
                print(num2[0])


                # msg = 'Hello, ' + str(name1[0]) + '! Great news, you have been matched with ' + str(name2[0]) + ' for ' + str(req[3])
                # msg += '. Please visit https://mealswap.onrender.com/exchanges to view more details about your exchange.'

                def create_message(name1, name2, place):
                    msg = 'Hello, ' + name1 + '! Great news, you have been matched with ' + name2 + ' for ' + req[3]
                    msg += ' at ' + place + '. Please visit https://mealswap.onrender.com/exchanges to view more details about your exchange.'
                    return msg

                if num1[0] in numbers and num2[0] in numbers:           
                    notifications.send_message(num1[0], create_message(name1[0], name2[0], place2[0]))
                    notifications.send_message(num2[0], create_message(name2[0], name1[0], place1[0]))



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
                    "SELECT * FROM exchanges WHERE reqid = %s", [id])
                
                exchange = cursor.fetchone()

                netid = exchange[1]
                swapid = exchange[2]    

                cursor.execute(
                    "SELECT * FROM users WHERE netid = %s", [netid])  

                row = cursor.fetchone()
                name1 = row[1]  
                place1 = row[4]  

                cursor.execute(
                    "SELECT phone FROM users WHERE netid = %s", [netid])  
                
                phone = cursor.fetchone()
                num1 = phone[0]

                cursor.execute(
                    "SELECT * FROM users WHERE netid = %s", [swapid])  

                row = cursor.fetchone()
                name2 = row[1]  
                place2 = row[4]  

                cursor.execute(
                    "SELECT phone FROM users WHERE netid = %s", [swapid])  
                
                phone = cursor.fetchone()
                num2 = phone[0]

                cursor.execute(
                    "DELETE FROM exchanges WHERE reqid = %s", [id])

                def create_message(name1, name2, place):
                    msg = 'Hello, ' + name1 + '! Unfortunately, your exchange with ' + name2 + ' at ' + place + ' has been cancelled. '
                    msg += 'Please visit https://mealswap.onrender.com/exchanges to view your current exchanges.'
                    return msg

                print(num1)
                print(name1)
                print(name2)
                print(place2)

                if num1 in numbers and num2 in numbers: 
                    notifications.send_message(num1, create_message(name1, name2, place2))
                    notifications.send_message(num2, create_message(name2, name1, place1))

                


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

                cursor.execute("INSERT INTO blocked (netid, block_netid) "
                    + "VALUES (%s, %s)", [username, netid])

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

def unblock_user(blockid, username):
    
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM blocked WHERE blockid = %s", [blockid])

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

def complete_exchange(id):
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM exchanges WHERE reqid = %s', [id])
    
    except Exception as ex:
        print(ex, file = sys.stderr)
        sys.exit(1)


def get_exchanges(username):
    username = str(username)
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                requested = []

                cursor.execute(
                    "SELECT * FROM exchanges WHERE (netid = %s OR swapnetid = %s) AND netid NOT IN (SELECT block_netid FROM blocked WHERE netid = %s) AND swapnetid NOT IN (SELECT block_netid FROM blocked WHERE netid = %s) AND netid NOT IN (SELECT netid FROM blocked WHERE block_netid = %s) AND swapnetid NOT IN (SELECT netid FROM blocked WHERE block_netid = %s)", [username, username, username, username, username, username])

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
                        nickname = user[2]
                        name = user[1]
                        plan = user[3]
                        phone = user[4]
                        request = [exchange_id, swapnetid, name, nickname, plan, phone, times]
                        print(request)
                        requested.append(request)

                return requested

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
        
        
        

def addBlockedUser(username, netid):
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:
            with connection.cursor() as cursor:
                lib = req_lib.ReqLib()

                req = lib.getJSON(
                    lib.configs.USERS_BASIC,
                    uid=netid,
                )
                print("here")
                if len(req) == 0:
                    return 1 # not a valid netid
                
                
                print(f'REQ CONTENTS: {req}')
                
                if netid == username:
                    return 2 # cannot be username
                
                
                cursor.execute(
                    "SELECT * FROM blocked WHERE netid=%s AND block_netid=%s", [username, netid])
                exists = cursor.fetchall()
                
                print(f'EXISTS: {exists}')
                if exists is not None and len(exists) > 0:
                    return 3 # cannot exist
                
                
                
                cursor.execute("INSERT INTO blocked (netid, block_netid) "
                               + "VALUES (%s, %s)", [username, netid])
                
                return 0

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

