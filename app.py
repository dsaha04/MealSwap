# https://pemagrg.medium.com/build-a-web-app-using-pythons-flask-for-beginners-f28315256893
# https://stackoverflow.com/questions/42465768/jinja2-template-not-found-and-internal-server-error

import server
import auth
from django.shortcuts import redirect

import flask
# from flask import Flask, request, render_template, jsonify, redirect, url_for

app = flask.Flask(__name__)

app.secret_key = '1234'


@app.route('/')
def home():
    return flask.render_template('login.html')


@app.route('/create', methods = ['GET', 'POST'])
def create():
    # TODO: fix logic to mirror submit_request
    username = auth.authenticate()
    if flask.request.method == 'POST':
        server.create_user(flask.request.form, username)
        return flask.redirect('/dashboard')
        
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
        netid = flask.request.form['netid']
        success = server.addBlockedUser(username, netid)
        
        if success == 1:
            flask.flash('that is not a valid netid')
            
        if success == 2:
            flask.flash('you cannot block yourself, silly :)')
         
        if success == 3:
            flask.flash('you\'ve already blocked this user')
        
        blocked = server.get_blocked(username)
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
    name = details[1]
    nickname = details[2]
    plan = details[3]
    number = details[4]
    return flask.render_template('profile_page.html', name = name, nickname = nickname, netid = str(username), dining_plan = plan, phone_no = number)

@app.route('/updatedetails', methods = ['GET', 'POST'])
def update_details():
    username = auth.authenticate()
    if flask.request.method == 'POST':
        server.update_details(flask.request.form, username)
        return flask.redirect("/profile")

    if server.check_user(username) != -1:
        return flask.render_template('update_details.html')       
    else: 
        return flask.redirect('/create')


@app.route('/blockuser', methods = ['GET', 'POST'])
def block_user():
    username = auth.authenticate()
    reqid = int(flask.request.form['reqid'])
    server.block_user(reqid, username)
    return flask.redirect("/profile")

@app.route('/unblock', methods = ['GET', 'POST'])
def unblock_user():
    username = auth.authenticate()
    blockid = int(flask.request.form['blockid'])
    server.unblock_user(blockid, username)
    
    instant_matched = server.check_for_instant_matches(username)
    if instant_matched:
        flask.flash(
            "You have just been instant-matched! Check the 'Your Exchanges' Page to see your new match Info.")
    
    blocked = server.get_blocked(username)
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
    print(req_table)
    
    if server.check_user(username) != -1:
        return flask.render_template('dashboard.html', table = req_table)       
    else: 
        return flask.redirect('/create')

@app.route('/yourrequests')
def your_requests():
    username = auth.authenticate()
    req_table = server.get_your_requests(username)
    
    return flask.render_template('your_requests.html', table= req_table)

@app.route('/exchanges')
def your_exchanges():
    username = auth.authenticate()
    req_table = server.get_exchanges(username)
    
    return flask.render_template('your_exchanges.html', table= req_table)

@app.route('/submitrequest', methods = ['GET', 'POST'])
def submit_request():
    username = auth.authenticate()
    
    if flask.request.method == 'POST':
        print('hi')
        
        response = server.create_request(flask.request.form, username)
        print(response)
        # DEBUGGING, delete
        if response:
            flask.flash(
                "You have just been instant-matched! Check the 'Your Exchanges' Page to see your new match Info.")
        return "easter egg :)"

    if server.check_user(username) != -1:
        return flask.render_template('submitrequest.html')       
    else: 
        return flask.redirect('/create')
    
@app.route('/viewrequest', methods = ['GET', 'POST'])
def view_request():
    username = auth.authenticate()
    
    reqid = flask.request.args.get('reqid')
    req = server.get_request(reqid)
    
    if flask.request.method == 'POST':
        print("REQUEST FORM:")
        print()
        reqid = int(flask.request.form['reqid'])
        server.accept_request(reqid, username)
        return flask.redirect('/exchanges')
    
    return flask.render_template('viewrequest.html', req=req)


@app.route('/deleterequest', methods = ['GET', 'POST'])
def delete_request():
    username = auth.authenticate()
    
    reqid = flask.request.args.get('reqid')
    req = server.get_request(reqid)
    
    if flask.request.method == 'POST':
        print("REQUEST FORM:")
        print()
        reqid = int(flask.request.form['reqid'])
        server.delete_request(reqid, username)
        
        print("FLASHED")
        return
    
    return flask.render_template('deleterequest.html', req=req)

@app.route('/undorequest', methods = ['GET', 'POST'])
def undo_request():
    username = auth.authenticate()
    
    reqid = int(flask.request.form['reqid'])
    print(f"TRYING TO GET REQUEST {reqid}")
    req = server.get_request(reqid)
    
    if flask.request.method == 'POST':
        print("UNDOing REQUEST")
        print(f'req: {req[1]}')
        server.undo_request(reqid, username)
        
        instant_matched = server.check_for_instant_matches(req[1])
        if instant_matched:
            flask.flash(
                "You have just been instant-matched! Check the 'Your Exchanges' Page to see your new match Info.")
        reqid = int(flask.request.form['reqid'])
        
        return "easter egg 2"
    
    return flask.render_template('undorequest.html', req=req)

@app.route('/trashrequest', methods = ['GET', 'POST'])
def trash_request():
    username = auth.authenticate()
    req_table = server.trash_requests(username)
    
    if server.check_user(username) != -1:
        return flask.render_template('trashrequest.html', table = req_table)       
    else: 
        return flask.redirect('/create')

@app.route('/cancelexchange', methods = ['GET', 'POST'])
def cancel_exchange():
    username = auth.authenticate()
    
    reqid = flask.request.args.get('reqid')
    req = server.get_exchange(reqid)
    
    if flask.request.method == 'POST':
        reqid = int(flask.request.form['reqid'])
        server.cancel_exchange(reqid)
        return flask.redirect('/exchanges')
    
    return flask.render_template('cancelexchange.html', req=req)

@app.route('/completeexchange', methods = ['GET', 'POST'])
def complete_exchange():
    username = auth.authenticate()
    reqid = int(flask.request.form['reqid'])
    server.complete_exchange(reqid)
    return flask.redirect('/exchanges')
    


@app.route('/cancelrequest', methods = ['GET', 'POST'])
def cancel_request():
    username = auth.authenticate()
    
    reqid = flask.request.args.get('reqid')
    req = server.get_request(reqid)
    
    if flask.request.method == 'POST':
        reqid = int(flask.request.form['reqid'])
        server.cancel_request(reqid)
        return flask.redirect('/dashboard')
    
    return flask.render_template('cancelrequest.html', req=req)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

