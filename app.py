import server
import auth
from django.shortcuts import redirect
import os
import flask
import flask_wtf.csrf

app = flask.Flask(__name__)

# TODO
app.secret_key = os.getenv('APP_SECRET_KEY')

flask_wtf.csrf.CSRFProtect(app)


@app.route('/')
def home():
    return flask.render_template('login.html')


@app.route('/create', methods = ['GET', 'POST'])
def create():
    print('creating acc')
    print(flask.request.form)
    username = auth.authenticate()
    if flask.request.method == 'POST':
        print(flask.request.form.to_dict())
        success = server.create_user(flask.request.form.to_dict(), username)

        if success == 0:
            return flask.render_template('error.html')
        
        if success == -1:
            return flask.render_template('errorparam.html')

        if success == -2:
            return flask.render_template('erroruser.html')
        
    check = server.check_user(username)

    if check == 0:
        return flask.redirect('/dashboard')
    elif check == -1: 
        return flask.render_template('create_account.html')
    elif check == -2:
        return flask.render_template('erroruser.html')
    else:
        return flask.render_template('error.html')        
        
@app.route('/logoutapp', methods=['GET'])
def logoutapp():
    return auth.logoutapp()

@app.route('/logoutcas', methods=['GET'])
def logoutcas():
    return auth.logoutcas()


@app.route('/blocked', methods=['GET', 'POST'])
def blocked():
    username = auth.authenticate()
    if server.check_user(username) == -1:
        return flask.redirect('/create')
    
    if flask.request.method == 'POST':
        if flask.request.form['server'] == 'search':
            print("post request")
            netid = flask.request.form['netid'].strip()
            success = server.addBlockedUser(username, netid)
            
            if success == 1:
                flask.flash('that is not a valid netid')
                
            if success == 2:
                flask.flash('you cannot block yourself, silly :)')
            
            if success == 3:
                flask.flash('you\'ve already blocked this user')
            
            if success == -1:
                return flask.render_template('erroruser.html')

        elif flask.request.form['server'] == 'user':
            reqid = int(flask.request.form['reqid'])
            success = server.block_user(reqid, username)
        elif flask.request.form['server'] == 'unblock':
            blockid = int(flask.request.form['blockid'])
            success = server.unblock_user(blockid, username)
            if success == 0:
                return flask.render_template('error.html')
            instant_matched = server.check_for_instant_matches(username)
            if instant_matched == -1:
                return flask.render_template('error.html')
            if instant_matched == -2:
                return flask.render_template('erroruser.html')
            if instant_matched:
                flask.flash(
                    "You have just been instant-matched! Check the 'Your Exchanges' Page to see your new match Info.")

        if success == 0:
            return flask.render_template('error.html')
        if success == -1:
            return flask.render_template('errorparam.html')
        if success == -2:
            return flask.render_template('erroruser.html')
   
    blocked = server.get_blocked(username)
    if blocked == 0:
        return flask.render_template('error.html')
    
    elif blocked == -1:
        return flask.render_template('erroruser.html')

    else:
        return flask.render_template('blocked.html', table = blocked)

@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    username = auth.authenticate()
    if server.check_user(username) == -1:
        return flask.redirect('/create')
    if flask.request.method == 'POST':
        success = server.update_details(flask.request.form.to_dict(), username)
        if success == 0:
            return flask.render_template('error.html')
        if success == -1:
            return flask.render_template('errorparam.html')
        if success == -2:
            return flask.render_template('erroruser.html')
        flask.flash(
            "You have successfully changed your profile information.")
        return flask.redirect('/dashboard')
    
    details = server.profile_details(username)
    if details == 0:
        return flask.render_template('error.html')
    if details == -1:
        return flask.render_template('erroruser.html')
    name = details[1]
    nickname = details[2]
    plan = details[3]
    number = details[4]
    return flask.render_template('profile_page.html', name = name, nickname = nickname, netid = str(username), dining_plan = plan, phone_no = number)

@app.route('/about')
def about():
    return flask.render_template('about.html')

@app.route('/tutorial')
def tutorial():
    return flask.render_template('tutorial.html')

@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard():
    username = auth.authenticate()
    print('in dashboard')
    if flask.request.method == 'POST':
        reqid = int(flask.request.form['reqid'])
        if flask.request.form['server'] == 'accept':
            success = server.accept_request(reqid, username)
            if success == 1:
                flask.flash(
                "You cannot have more than 5 pending exchanges at one time.")
            elif success ==2:
                flask.flash("This request has been accepted! Please navigate to your exchanges to view more details about this exchange.")
        elif flask.request.form['server'] == 'decline':
            success = server.delete_request(reqid, username)
            flask.flash("That request has been sent to the trash. To undo this, go to the \'Decline Requests\' Page. ")
        
        if success == 0:
            return flask.render_template('error.html')
        elif success == -1:
            flask.render_template('errorparam.html')
        elif success == -2:
            flask.render_template('erroruser.html')

    req_table = server.get_requests(username) 
    if req_table == 0:
            return flask.render_template('error.html') 
    if req_table == -1:
        return flask.render_template('erroruser.html') 
    if server.check_user(username) != -1:
        print('checked')
        return flask.render_template('dashboard.html', table = req_table)       
    else: 
        return flask.redirect('/create')

@app.route('/yourrequests', methods = ['GET', 'POST'])
def your_requests():
    username = auth.authenticate()
    if server.check_user(username) == -1:
        return flask.redirect('/create')
    if flask.request.method == 'POST':
        reqid = int(flask.request.form['reqid'])
        success = server.cancel_request(reqid)
        if success == 0:
            return flask.render_template('error.html')
        elif success == -1:
            return flask.render_template('errorparam.html')
    req_table = server.get_your_requests(username)
    if req_table == 0:
        return flask.render_template('error.html')

    if req_table == -1:
        return flask.render_template('erroruser.html') 

    return flask.render_template('your_requests.html', table= req_table)

@app.route('/exchanges', methods = ['GET', 'POST'])
def your_exchanges():
    username = auth.authenticate()
    if server.check_user(username) == -1:
        return flask.redirect('/create')
    if flask.request.method == 'POST':
        reqid = int(flask.request.form['reqid'])
        if flask.request.form['server'] == 'cancel':
            success = server.cancel_exchange(reqid)
        if flask.request.form['server'] == 'complete':
            success = server.complete_exchange(reqid, username)
            if success == -2:
                return flask.render_template('erroruser.html')
        if success == 0:
            return flask.render_template('error.html')
        elif success == -1:
            return flask.render_template('errorparam.html')

    req_table = server.get_exchanges(username)
    print(req_table)
    if req_table == 0:
        return flask.render_template('error.html')
    if req_table == -1:
        return flask.render_template('erroruser.html')
    
    return flask.render_template('your_exchanges.html', table= req_table)

@app.route('/submitrequest', methods = ['GET', 'POST'])
def submit_request():
    username = auth.authenticate()
    
    if flask.request.method == 'POST':
        print('hi')
        
        response = server.create_request(flask.request.form.to_dict(), username)
        print(f'RESPONSE: {response}')
        # DEBUGGING, delete
        if response == 0:
            return flask.render_template('error.html')
        if response == -1:
            return flask.render_template('errorparam.html')
        if response == -2:
            return flask.render_template('erroruser.html')
        if response == 1:
            print("flashing...")
            flask.flash(
                "You cannot have more than 5 pending requests/exchanges. Please cancel some of your requests or complete some of your exchanges to submit more requests.")
            return flask.redirect('/yourrequests')
        
        if response == 2:
            flask.flash(
                "You have just been instant-matched! Check the 'Your Exchanges' Page to see your new match Info.")
            return flask.redirect('/exchanges')
            
        return flask.redirect('/yourrequests')
    
    check = server.check_user(username)

    if check == 0:
        return flask.render_template('submitrequest.html')       
    elif check == -1: 
        return flask.redirect('/create')
    elif check == -2:
        return flask.render_template('erroruser.html')
    else:
        return flask.render_template('error.html')
    
@app.route('/trashrequest', methods = ['GET', 'POST'])
def trash_request():
    username = auth.authenticate()
    if flask.request.method == 'POST':
        reqid = int(flask.request.form['reqid'])
        req = server.get_request(reqid)
        if req == 0:
            return flask.render_template('error.html')
        if req == -1:
            return flask.render_template('errorparam.html')
        success = server.undo_request(reqid, username)
        if success == 0:
            return flask.render_template('error.html')
        elif success == -1:
            return flask.render_template('errorparam.html')
        elif success == -2:
            return flask.render_template('erroruser.html')
        
        instant_matched = server.check_for_instant_matches(req[1])
        if instant_matched == -1:
            return flask.render_template('error.html')
        if instant_matched == -2:
            return flask.render_template('erroruser.html')
        if instant_matched:
            flask.flash(
                "You have just been instant-matched! Check the 'Your Exchanges' Page to see your new match Info.")

        if not instant_matched:
            flask.flash(
                "Successfully undone the trashed request ")
    req_table = server.trash_requests(username)
    if req_table == 0:
        return flask.render_template('error.html')

    if req_table == -1:
        return flask.render_template('erroruser.html')   

    check = server.check_user(username)

    if check == 0:
        return flask.render_template('trashrequest.html', table = req_table)       
    elif check == -1: 
        return flask.redirect('/create')
    elif check == -2:
        return flask.render_template('erroruser.html')
    else:
        return flask.render_template('error.html')

@app.route('/getupdates', methods=['GET', 'POST'])
def get_updates():
    if flask.request.method == 'GET':
        return flask.redirect('/dashboard')
    username = auth.authenticate()
    timestamp, timestamp2 = server.getRequestBlocked(username)
    
    print(f'timestamp: {timestamp}, {timestamp2}')
    if timestamp == -1 or timestamp2 == -1:
        return flask.render_template('error.html')
    if timestamp == -2 or timestamp2 == -2:
        return flask.render_template('erroruser.html')
    
    
    return [timestamp, timestamp2]

@app.route('/getexchangeupdates', methods=['POST'])
def get_exchange_updates():
    if flask.request.method == 'GET':
        return flask.redirect('/dashboard')
    username = auth.authenticate()
    
    timestamp, timestamp2 = server.getExchangeBlocked(username)

    print(f'timestamp: {timestamp}, {timestamp2}')
    if timestamp == -1 or timestamp2 == -1:
        return flask.render_template('error.html')
    if timestamp == -2 or timestamp2 == -2:
        return flask.render_template('erroruser.html')

    return [timestamp, timestamp2]
    

@app.route('/getrequestupdates', methods=['GET', 'POST'])
def get_request_updates():
    if flask.request.method == 'GET':
        return flask.redirect('/dashboard')
    username = auth.authenticate()

    timestamp = server.getNumRequests(username)

    print(f'request timestamp: {timestamp}')
    
    if timestamp == -1:
        return flask.render_template('error.html')
    if timestamp == -2:
        return flask.render_template('erroruser.html')

    return [timestamp]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

