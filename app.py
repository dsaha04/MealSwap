# https://pemagrg.medium.com/build-a-web-app-using-pythons-flask-for-beginners-f28315256893
# https://stackoverflow.com/questions/42465768/jinja2-template-not-found-and-internal-server-error

import server
import auth
from django.shortcuts import redirect
import os
# from dotenv import load_dotenv

# load_dotenv()

import flask
# from flask import Flask, request, render_template, jsonify, redirect, url_for
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
    # TODO: fix logic to mirror submit_request
    print('creating acc')
    print(flask.request.form)
    username = auth.authenticate()
    if flask.request.method == 'POST':
        print(flask.request.form.to_dict())
        success = server.create_user(flask.request.form.to_dict(), username)

        if success == 0:
            return flask.render_template('error.html')
        
    if server.check_user(username) == -1:
        return flask.render_template('create_account.html')

    else:
        # fix url
        return flask.redirect('/dashboard')
        

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
        print("post request")
        netid = flask.request.form['netid'].strip()
        success = server.addBlockedUser(username, netid)

        if success == 0:
            return flask.render_template('error.html')
        
        if success == 1:
            flask.flash('that is not a valid netid')
            
        if success == 2:
            flask.flash('you cannot block yourself, silly :)')
         
        if success == 3:
            flask.flash('you\'ve already blocked this user')
        
        blocked = server.get_blocked(username)
        if blocked == 0:
            return flask.render_template('error.html')
        print(blocked)
        return flask.render_template('blocked.html', table = blocked)
        
    blocked = server.get_blocked(username)
    return flask.render_template('blocked.html', table = blocked)

@app.route('/profile')
def profile():
    username = auth.authenticate()
    if server.check_user(username) == -1:
        return flask.redirect('/create')
    details = server.profile_details(username)
    if details == 0:
        return flask.render_template('error.html')
    name = details[1]
    nickname = details[2]
    plan = details[3]
    number = details[4]
    return flask.render_template('profile_page.html', name = name, nickname = nickname, netid = str(username), dining_plan = plan, phone_no = number)

@app.route('/updatedetails', methods = ['GET', 'POST'])
def update_details():
    username = auth.authenticate()
    if flask.request.method == 'POST':
        success = server.update_details(flask.request.form.to_dict(), username)
        if success == 0:
            return flask.render_template('error.html')
        return flask.redirect("/dashboard")

    if server.check_user(username) != -1:
        return flask.render_template('update_details.html')       
    else: 
        return flask.redirect('/create')


@app.route('/blockuser', methods = ['GET', 'POST'])
def block_user():
    username = auth.authenticate()
    reqid = int(flask.request.form['reqid'])
    if flask.request.method == 'POST':
        success = server.block_user(reqid, username)
        if success == 0:
            return flask.render_template('error.html')
    return flask.redirect("/blocked")

@app.route('/unblock', methods = ['GET', 'POST'])
def unblock_user():
    username = auth.authenticate()
    blockid = int(flask.request.form['blockid'])
    success = server.unblock_user(blockid, username)
    if success == 0:
        return flask.render_template('error.html')
    
    instant_matched = server.check_for_instant_matches(username)
    if instant_matched == -1:
        return flask.render_template('error.html')
    if instant_matched:
        flask.flash(
            "You have just been instant-matched! Check the 'Your Exchanges' Page to see your new match Info.")
    
    blocked = server.get_blocked(username)
    if blocked == 0:
            return flask.render_template('error.html')
    return flask.render_template('blocked.html', table=blocked)



@app.route('/test')
def test():
    return flask.render_template('test.html')

'''
@app.route('/create-new-user', methods=['GET', 'POST'])
def my_form_post():
   if request.method == 'POST':
       firstname = request.form['firstname']
       result = {
           "output": firstname
       }

       server.create_user(request.form, username)

        
    
        
        TODO: ADD TO DATABASE HERE
        
        TODO; Redirect the user instead of calling jsonify
        
       return jsonify(result=result)

   return render_template('create_account.html')
'''

@app.route('/about')
def about():
    return flask.render_template('about.html')

@app.route('/tutorial')
def tutorial():
    return flask.render_template('tutorial.html')

@app.route('/dashboard')
def dashboard():
    username = auth.authenticate()
    req_table = server.get_requests(username) 
    if req_table == 0:
            return flask.render_template('error.html')   
    if server.check_user(username) != -1:
        return flask.render_template('dashboard.html', table = req_table)       
    else: 
        return flask.redirect('/create')

@app.route('/yourrequests')
def your_requests():
    username = auth.authenticate()
    req_table = server.get_your_requests(username)
    if req_table == 0:
        return flask.render_template('error.html')
    
    return flask.render_template('your_requests.html', table= req_table)

@app.route('/exchanges')
def your_exchanges():
    username = auth.authenticate()
    req_table = server.get_exchanges(username)
    if req_table == 0:
        return flask.render_template('error.html')
    
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
        if response == 1:
            print("flashing...")
            flask.flash(
                "You cannot open more than 5 pending requests")
            return flask.redirect('/yourrequests')
        
        if response == 2:
            flask.flash(
                "You have just been instant-matched! Check the 'Your Exchanges' Page to see your new match Info.")
            return flask.redirect('/exchanges')
            
        return flask.redirect('/yourrequests')

    if server.check_user(username) != -1:
        return flask.render_template('submitrequest.html')       
    else: 
        return flask.redirect('/create')
    
@app.route('/viewrequest', methods = ['GET', 'POST'])
def view_request():
    username = auth.authenticate()
    
    reqid = flask.request.args.get('reqid')
    req = server.get_request(reqid)
    if req == 0:
        return flask.render_template('error.html')
    
    if flask.request.method == 'POST':
        print("REQUEST FORM:")
        print()
        reqid = int(flask.request.form['reqid'])
        success = server.accept_request(reqid, username)
        if success == 0:
            return flask.render_template('error.html')

        return flask.redirect('/exchanges')
    
    # return flask.render_template('viewrequest.html', req=req)


@app.route('/deleterequest', methods = ['GET', 'POST'])
def delete_request():
    username = auth.authenticate()
    
    reqid = flask.request.args.get('reqid')
    req = server.get_request(reqid)
    if req == 0:
        return flask.render_template('error.html')
    
    if flask.request.method == 'POST':
        print("REQUEST FORM:")
        print()
        reqid = int(flask.request.form['reqid'])
        success = server.delete_request(reqid, username)
        if success == 0:
            return flask.render_template('error.html')
        
        print("FLASHED")
        return flask.redirect('/dashboard')
    
    return flask.render_template('deleterequest.html', req=req)

@app.route('/undorequest', methods = ['GET', 'POST'])
def undo_request():
    username = auth.authenticate()
    
    reqid = int(flask.request.form['reqid'])
    print(f"TRYING TO GET REQUEST {reqid}")
    req = server.get_request(reqid)
    if req == 0:
        return flask.render_template('error.html')
    
    if flask.request.method == 'POST':
        print("UNDOing REQUEST")
        print(f'req: {req[1]}')
        success = server.undo_request(reqid, username)
        if success == 0:
            return flask.render_template('error.html')
        
        instant_matched = server.check_for_instant_matches(req[1])
        if instant_matched == -1:
            return flask.render_template('error.html')
        if instant_matched:
            flask.flash(
                "You have just been instant-matched! Check the 'Your Exchanges' Page to see your new match Info.")
        reqid = int(flask.request.form['reqid'])
        
        return flask.redirect('/dashboard')
    
    return flask.render_template('undorequest.html', req=req)

@app.route('/trashrequest', methods = ['GET', 'POST'])
def trash_request():
    username = auth.authenticate()
    req_table = server.trash_requests(username)
    if req_table == 0:
        return flask.render_template('error.html')
    
    if server.check_user(username) != -1:
        return flask.render_template('trashrequest.html', table = req_table)       
    else: 
        return flask.redirect('/create')

@app.route('/cancelexchange', methods = ['GET', 'POST'])
def cancel_exchange():
    username = auth.authenticate()
    
    reqid = flask.request.args.get('reqid')
    req = server.get_exchange(reqid)
    if req == 0:
        return flask.render_template('error.html')
    
    if flask.request.method == 'POST':
        reqid = int(flask.request.form['reqid'])
        success = server.cancel_exchange(reqid)
        if success == 0:
            return flask.render_template('error.html')
        return flask.redirect('/exchanges')
    
    return flask.render_template('cancelexchange.html', req=req)

@app.route('/completeexchange', methods = ['GET', 'POST'])
def complete_exchange():
    username = auth.authenticate()
    reqid = int(flask.request.form['reqid'])
    success = server.complete_exchange(reqid)
    if success == 0:
        return flask.render_template('error.html')
    return flask.redirect('/exchanges')
    


@app.route('/cancelrequest', methods = ['GET', 'POST'])
def cancel_request():
    username = auth.authenticate()
    
    reqid = flask.request.args.get('reqid')
    req = server.get_request(reqid)
    if req == 0:
        return flask.render_template('error.html')
    
    if flask.request.method == 'POST':
        reqid = int(flask.request.form['reqid'])
        success = server.cancel_request(reqid)
        if success == 0:
            return flask.render_template('error.html')
        return flask.redirect('/yourrequests')
    
    return flask.redirect('/dashboard')


@app.route('/getupdates', methods=['GET', 'POST'])
def get_updates():
    username = auth.authenticate()
    timestamp = server.getMostRecentTimestamp(username)
    if timestamp == 0:
        return flask.render_template('error.html')
    return [timestamp]
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

