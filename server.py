import sys
import app
import os
import psycopg2
import notifications
import req_lib
import sqlalchemy
import sqlalchemy.orm
import createorm

numbers = {'6506958443', '2485332973', '2489466588', '2019522343', '3124592594', '7035019474', '6092582211', '2672261984', '7328533443', '2157422798'}

DATABASE_URL = os.getenv('DATABASE_URL')

engine = sqlalchemy.create_engine(DATABASE_URL)

def create_user(details, netid):
    if 'plan' not in details.keys() or 'name' not in details.keys() or 'number' not in details.keys() or not details['plan'] or not details['name'] or not details['number']:
        return -1
    if  not netid:
        return -2
    netid = str(netid)
    print(f'details: {details}')
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

        with sqlalchemy.orm.Session(engine) as session:

            user = createorm.Users(netid = netid, name = name, nickname = nickname, plan = plan, phone = phone)
            session.add(user)
            session.commit()

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0

def get_blocked(username):
    if not username:
        return -1
    try:

        with sqlalchemy.orm.Session(engine) as session:

            query = (session.query(createorm.Blocked).filter(createorm.Blocked.netid == username))
            rows = query.all()
            print(rows)
            table = []

            if rows is not None:
                for row in rows:
                    print(row)
                    lib = req_lib.ReqLib()

                    req = lib.getJSON(
                        lib.configs.USERS_BASIC,
                        uid=row.block_netid,
                    )
                    name = ['', '', '']
                    
                    if len(req) != 0:
                        print(req[0]['displayname'])
                    
                    name = [0, 0, 0, 0]
                    table.append(
                        [row.blockid, row.block_netid, req[0]['displayname'], name[2]])
        return table
        
    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0


def update_details(details, netid):

    if 'plan' not in details.keys() or 'name' not in details.keys() or 'number' not in details.keys():
        return -1
    if not netid:
        return -2

    usersOld = profile_details(netid)

    netid = str(netid)
    nickname = str(usersOld[2])
    plan = str(usersOld[3]) 
    phone = str(usersOld[4])
    print(details)

    if details['plan'] != "":
        plan = str(details['plan'])

    if details['name'] != "":
        name = str(details['name'])

    if details['number'] != "":
        phone = str(details['number'])

    users = (name, plan, phone, netid)

    try:

        with sqlalchemy.orm.Session(engine) as session:

            query = (session.query(createorm.Users).filter(createorm.Users.netid == netid))
            row = query.one_or_none()
            row.nickname = name
            row.plan = plan
            row.phone = phone
            session.commit()
        
    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0

def check_user(username):
    if not username:
        return -2
    print('checking')

    username = str(username)
    try:
        with sqlalchemy.orm.Session(engine) as session:

            query = (session.query(createorm.Users).filter(createorm.Users.netid == username))

            row = query.one_or_none()
            if row is None:
                return -1
            else:
                return 0
            
    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 1

def check_for_instant_matches(username):
    if not username:
        return -2
    
    try:
        with sqlalchemy.orm.Session(engine) as session:

            query = (session.query(createorm.Users).filter(createorm.Users.netid == username))
            row = query.one_or_none()
            matched = False
            if row is not None:
                user_plan = row.plan
                print(user_plan)

                query = (session.query(createorm.Requested).filter(createorm.Requested.netid == username))
                table = query.all()
                print(table)
                if table is not None:
                    print('xx')
                    for request in table:
                        plan = request.requested
                        time = request.times
                        query = (session.query(createorm.Requested).filter(createorm.Requested.requested == user_plan).filter(createorm.Requested.times == time))
                        matches = query.all()
                        if matches is not None:
                            for match in matches:
                                netid = match.netid
                                query = (session.query(createorm.Blocked).filter(createorm.Blocked.netid == username).filter(createorm.Blocked.block_netid == netid))
                                print(query.count())
                                blocked = query.one_or_none()
                                if blocked is not None:
                                    print('xy')
                                    continue
                                query = (session.query(createorm.Blocked).filter(createorm.Blocked.netid == netid).filter(createorm.Blocked.block_netid == username))
                                print(query.count())
                                blocked = query.one_or_none()
                                if blocked is not None:
                                    print('xz')
                                    continue     
                                reqid = match.reqid
                                print(reqid)
                                query = (session.query(createorm.Deletedrequest).filter(createorm.Deletedrequest.reqid == reqid).filter(createorm.Deletedrequest.netid == username))
                                print(query.count())
                                deleted = query.one_or_none()
                                if deleted is not None:
                                    print('yz')
                                    continue
                                if netid != username:
                                    query = (session.query(createorm.Users).filter(createorm.Users.netid == netid))
                                    print(query.count())
                                    user = query.one_or_none()
                                    if plan == user.plan:
                                        print('match')
                                        accept_request(int(reqid), username)
                                        matched = True
                                        break
            
        return matched
            
    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return -1

def create_request(details, username):

    if 'plan' not in details.keys() or 'times' not in details.keys() or not details['plan'] or not details['times']:
        return -1
    
    if not username:
        return -2

    username = str(username)
    requested_plan = details['plan']
    times = details['times']

    try:
        with sqlalchemy.orm.Session(engine) as session:
            count = (session.query(createorm.Requested).filter(createorm.Requested.netid == username)).count()
            exchange1 = (session.query(createorm.Exchanges).filter(createorm.Exchanges.netid == username)).count()
            exchange2 = (session.query(createorm.Exchanges).filter(createorm.Exchanges.swapnetid == username)).count()

            if count + exchange1 + exchange2 >= 5:
                return 1 # you cannot make more than 5 requests
            request = createorm.Requested(netid = username, requested = requested_plan, times = times)
            session.add(request)
            session.commit()

            match = check_for_instant_matches(username)
            if match:
                query = (session.query(createorm.Requested).filter(createorm.Requested.netid == username).filter(createorm.Requested.requested == requested_plan).filter(createorm.Requested.times == times))
                query.delete()
                session.commit()
                return 2

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0

def profile_details(username):

    if not username:
        return -1

    username = str(username)
    try:
        with sqlalchemy.orm.Session(engine) as session:
            
            query = (session.query(createorm.Users).filter(createorm.Users.netid == username))
            row = query.one()

            return [row.netid, row.name, row.nickname, row.plan, row.phone]     

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0

def get_requests(username):

    if not username:
        return -1

    username = str(username)
    try:
        with sqlalchemy.orm.Session(engine) as session:

            requested = []

            query = (session.query(createorm.Users).filter(createorm.Users.netid == username))
            user = query.one_or_none()
            if user is not None:
                plan = user.plan

                query = (session.query(createorm.Requested).filter(createorm.Requested.requested == plan).filter(createorm.Requested.netid != username))
                rows = query.all()

                query = (session.query(createorm.Deletedrequest).filter(createorm.Deletedrequest.netid == username))
                deleted = query.all()
            
                if rows is not None:
                    for row in rows:
                        reqid = row.reqid
                        netid = row.netid

                        query = (session.query(createorm.Blocked).filter(createorm.Blocked.netid == username).filter(createorm.Blocked.block_netid == netid))
                        blocked = query.one_or_none()
                        if blocked is not None:
                            continue
                        query = (session.query(createorm.Blocked).filter(createorm.Blocked.netid == netid).filter(createorm.Blocked.block_netid == username))
                        blocked = query.one_or_none()
                        if blocked is not None:
                            continue  

                        flag = False
                        for delete in deleted:
                            if reqid == delete.reqid:
                                flag = True
                                break
                        
                        if flag:
                            continue
                        requested_dining_plan = row.requested
                        times = row.times
                        query = (session.query(createorm.Users).filter(createorm.Users.netid == netid))
                        user = query.one_or_none()
                        offer_dining_plan = user.plan

                        request = [requested_dining_plan, offer_dining_plan, times, netid, reqid]
                    
                        requested.append(request)

            return requested    
            
    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0

def trash_requests(username):

    if not username:
        return -1

    username = str(username)
    try:
        with sqlalchemy.orm.Session(engine) as session:
            requested = []
            query = (session.query(createorm.Deletedrequest).filter(createorm.Deletedrequest.netid == username))
            deleted = query.all()

            if deleted is not None:
                for delete in deleted:
                    reqid = delete.reqid
                    query = (session.query(createorm.Requested).filter(createorm.Requested.reqid == reqid))
                    row = query.one_or_none()

                    if row is not None:
                        netid = row.netid
                        requested_dining_plan = row.requested
                        times = row.times
                        query = (session.query(createorm.Users).filter(createorm.Users.netid == netid))
                        user = query.one_or_none()
                        offer_dining_plan = user.plan
                        request = [requested_dining_plan, offer_dining_plan, times, netid, reqid]
                        requested.append(request)

            return requested    
            
    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0


def get_your_requests(username):
    if not username:
        return -1
    username = str(username)
    try:
        with sqlalchemy.orm.Session(engine) as session:

            requested = []
            query = (session.query(createorm.Requested).filter(createorm.Requested.netid == username))
            rows = query.all()

            if rows is not None:
                for row in rows:
                    reqid = row.reqid
                    netid = row.netid
                    requested_dining_plan = row.requested
                    times = row.times
                    request = [requested_dining_plan, times, netid, reqid]
                    requested.append(request)

            return requested
            
    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0
            
def get_request(id):
    if not isinstance(id, int):
        return -1
    print('in here')
    try:
        with sqlalchemy.orm.Session(engine) as session:

            print("ID")
            print(id)
            query = (session.query(createorm.Requested).filter(createorm.Requested.reqid == id))
            req = query.one_or_none()
            requested = [req.reqid, req.netid, req.requested, req.times, req.created_at]    
            return requested

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0


def accept_request(id, username):
    if not isinstance(id, int):
        return -1
    if not username:
        return -2
    print("accepting request")
    
    try:
        with sqlalchemy.orm.Session(engine) as session:

            count1 = (session.query(createorm.Exchanges).filter(createorm.Exchanges.netid == username)).count()
            count2 = (session.query(createorm.Exchanges).filter(createorm.Exchanges.swapnetid == username)).count()
            count3 = (session.query(createorm.Requested).filter(createorm.Requested.netid == username)).count()
            if (count1 + count2 + count3) >= 5:
                return 1 # you cannot make more than 5 requests

            requested = []
            print("ID")
            print(id)
            query = (session.query(createorm.Requested).filter(createorm.Requested.reqid == id))
            req = query.one_or_none()            
            info = (id, username, req.netid, req.times, "FALSE")
            print("INFO")
            print(info)

            exchange = createorm.Exchanges(reqid = id, netid = username, swapnetid = req.netid, times = req.times, completed = "FALSE")
            session.add(exchange)
            session.commit()

            query = (session.query(createorm.Users).filter(createorm.Users.netid == username))
            user = query.one_or_none()
            num1 = user.phone
            name1 = user.name
            place1 = user.plan

            query = (session.query(createorm.Users).filter(createorm.Users.netid == req.netid))
            user = query.one_or_none()
            num2 = user.phone
            name2 = user.name
            place2 = user.plan

            query = (session.query(createorm.Requested).filter(createorm.Requested.reqid == id))
            query.delete()
            session.commit()

            def create_message(name1, name2, place):
                msg = 'Hello, ' + name1 + '! Great news, you have been matched with ' + name2 + ' for ' + req.times
                msg += ' at ' + place + '. Please visit https://mealswap.onrender.com/exchanges to view more details about your exchange.'
                return msg

            if num1 in numbers and num2 in numbers:           
                notifications.send_message(num1, create_message(name1, name2, place2))
                notifications.send_message(num2, create_message(name2, name1, place1))
            
            return 2

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0

def delete_request(id, username):

    if not isinstance(id, int):
        return -1
    if not username:
        return -2

    print("deleting request")
    
    try:
        with sqlalchemy.orm.Session(engine) as session:

            requested = []
            print("ID")
            print(id)
            print("REQ")
            print(username)
            
            info = (id, username)
            print("INFO")
            print(info)

            deletedrequest = createorm.Deletedrequest(reqid = id, netid = username)
            session.add(deletedrequest)
            session.commit()

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0


def cancel_exchange(id):

    if not isinstance(id, int):
        return -1
    print("cancelling exchange")
    
    try:
        with sqlalchemy.orm.Session(engine) as session:

            query = (session.query(createorm.Exchanges).filter(createorm.Exchanges.reqid == id))
            exchange = query.one_or_none()
            netid = exchange.netid
            swapid = exchange.swapnetid
            
            query = (session.query(createorm.Users).filter(createorm.Users.netid == netid))
            row = query.one_or_none()
            name1 = row.name
            place1 = row.plan
            num1 = row.phone

            query = (session.query(createorm.Users).filter(createorm.Users.netid == swapid))
            row = query.one_or_none()
            name2 = row.name
            place2 = row.plan
            num2 = row.phone

            query = (session.query(createorm.Exchanges).filter(createorm.Exchanges.reqid == id))
            query.delete()
            session.commit()

            def create_message(name1, name2, place):
                msg = 'Hello, ' + name1 + '! Unfortunately, your exchange with ' + name2 + ' at ' + place + ' has been cancelled. '
                msg += 'Please visit https://mealswap.onrender.com/exchanges to view your current exchanges.'
                return msg

            if num1 in numbers and num2 in numbers: 
                notifications.send_message(num1, create_message(name1, name2, place2))
                notifications.send_message(num2, create_message(name2, name1, place1))

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0


def cancel_request(id):

    if not isinstance(id, int):
        return -1 
    print("cancelling exchange")
    
    try:
        with sqlalchemy.orm.Session(engine) as session:
            
            query = (session.query(createorm.Requested).filter(createorm.Requested.reqid == id))
            query.delete()
            session.commit()

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0

def undo_request(id, username):

    if not isinstance(id, int):
        return -1
    if not username:
        return -2
    try:
        with sqlalchemy.orm.Session(engine) as session:

            query = (session.query(createorm.Deletedrequest).filter(createorm.Deletedrequest.reqid == id).filter(createorm.Deletedrequest.netid == username))
            query.delete()
            session.commit()

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0

def block_user(reqid, username):

    if not isinstance(reqid, int):
        return -1
    if not username:
        return -2
    try:
        with sqlalchemy.orm.Session(engine) as session:

            print(reqid)
            query = (session.query(createorm.Exchanges).filter(createorm.Exchanges.reqid == reqid))
            exchange = query.one_or_none()
            netid = exchange.netid
            if netid == username:
                netid = exchange.swapnetid
            
            blocked = createorm.Blocked(netid = username, block_netid = netid)
            session.add(blocked)
            session.commit()

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0

def unblock_user(blockid, username):

    if not isinstance(blockid, int):
        return -1
    if not username:
        return -2
    
    try:
        with sqlalchemy.orm.Session(engine) as session:
            query = (session.query(createorm.Blocked).filter(createorm.Blocked.blockid == blockid))
            query.delete()
            session.commit()

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0

def complete_exchange(id, username):

    if not isinstance(id, int):
        return -1
    if not username:
        return -2

    try:
        with sqlalchemy.orm.Session(engine) as session:

            query = (session.query(createorm.Exchanges).filter(createorm.Exchanges.reqid == id))
            row = query.one_or_none()
            netid = row.netid
            if netid == username:
                netid = row.swapnetid
            
            query = (session.query(createorm.Users).filter(createorm.Users.netid == netid))
            row = query.one_or_none()
            phone = row.phone
            name1 = row.name
            query = (session.query(createorm.Users).filter(createorm.Users.netid == username))
            row = query.one_or_none()
            name2 = row.name

            def create_message(name1, name2):
                if not name1 or not name2:
                    return -1
                msg = 'Hello, ' + name1 + '! ' + name2 + ' has marked your exchange as complete. Please visit https://mealswap.onrender.com/exchanges to view your pending exchanges.'
                return msg


            query = (session.query(createorm.Exchanges).filter(createorm.Exchanges.reqid == id))
            query.delete()
            session.commit()
            
            msg = create_message(name1, name2)
            if phone in numbers:           
                notifications.send_message(phone, msg)
    
    except Exception as ex:
        print(ex, file = sys.stderr)
        print(ex, "Server Error")
        return 0


def get_exchanges(username):
    if not username:
        return -1
    username = str(username)
    try:
        with sqlalchemy.orm.Session(engine) as session:

            requested = []

            query = (session.query(createorm.Exchanges).filter((createorm.Exchanges.netid == username) | (createorm.Exchanges.swapnetid == username)))
            rows = query.all()

            if rows is not None:
                for row in rows:

                    exchange_id = row.reqid
                    netid = row.netid
                    swapnetid = row.swapnetid

                    query = (session.query(createorm.Blocked).filter(createorm.Blocked.netid == netid).filter(createorm.Blocked.block_netid == swapnetid))
                    blocked = query.one_or_none()
                    if blocked is not None:
                        continue
                    
                    query = (session.query(createorm.Blocked).filter(createorm.Blocked.netid == swapnetid).filter(createorm.Blocked.block_netid == netid))
                    blocked = query.one_or_none()
                    if blocked is not None:
                        continue

                    times = row.times
                    completed = row.completed
                    if swapnetid == username:
                        swapnetid = netid
                    
                    query = (session.query(createorm.Users).filter(createorm.Users.netid == swapnetid))
                    user = query.one_or_none()
                    nickname = user.nickname
                    name = user.name
                    plan = user.plan
                    phone = user.phone
                    request = [exchange_id, swapnetid, name, nickname, plan, phone, times]
                    print(request)
                    requested.append(request)

            return requested

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0
        
def addBlockedUser(username, netid):
    if not netid.isalnum():
        return 1
    if not username:
        return -1
    try:

        with sqlalchemy.orm.Session(engine) as session:

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
                print('2')
                return 2 # cannot be username

            query = (session.query(createorm.Blocked).filter(createorm.Blocked.netid == username).filter(createorm.Blocked.block_netid == netid))
            exists = query.one_or_none()
            if exists is not None:    
                print('3') 
                return 3       
            
            print('4') 
            blocked = createorm.Blocked(netid = username, block_netid = netid)
            session.add(blocked)
            session.commit()

            return 4

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return 0

def getMostRecentTimestamp(username):

    if not username:
        return -2 
    
    try:
        with sqlalchemy.orm.Session(engine) as session:

            print('getting most recent timestamp...')

            query = (session.query(createorm.Users).filter(createorm.Users.netid == username))
            user = query.one_or_none()
            plan = user.plan
            print(f'plan: {plan}')
            count = (session.query(createorm.Requested).filter(createorm.Requested.requested == plan)).count()

            print(f'count: {count}')
            return count
            
    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return -1
    

def getMostRecentRequestTimestamp(username):

    if not username:
        return -2

    try:
        with sqlalchemy.orm.Session(engine) as session:

            print('getting most recent timestamp...')

            count = (session.query(createorm.Requested).filter(
                createorm.Requested.netid == username)).count()
            print(f'count: {count}')
            return count

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return -1
    
def getMostRecentBlockedTimestamp(username):

    if not username:
        return -2

    try:
        with sqlalchemy.orm.Session(engine) as session:

            print('getting most recent blocked timestamp...')

            count = (session.query(createorm.Blocked).filter(createorm.Blocked.block_netid == username)).count()

            print(f'blocked count: {count}')
            return count

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return -1

def getMostRecentExchangeTimestamp(username):

    if not username:
        return -2

    try:
        with sqlalchemy.orm.Session(engine) as session:

            print('getting most recent exchange timestamp...')

            count = (session.query(createorm.Exchanges).filter((createorm.Exchanges.swapnetid == username) | (createorm.Exchanges.netid == username))).count()
            
            print(f'count: {count}')
            return count

    except Exception as ex:
        print(ex, file=sys.stderr)
        print(ex, "Server Error")
        return -1

def getExchangeBlocked(username):
    if not username:
        return [-2,-2]
    t1 = getMostRecentExchangeTimestamp(username)
    t2 = getMostRecentBlockedTimestamp(username)

    return [t1, t2]

def getRequestBlocked(username):
    if not username:
        return [-2,-2]
    t1 = getMostRecentTimestamp(username)
    t2 = getMostRecentBlockedTimestamp(username)

    return [t1, t2]


def getNumRequests(username):
    if not username:
        return -2
    t1 = getMostRecentRequestTimestamp(username)

    return t1
