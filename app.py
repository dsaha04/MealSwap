# https://pemagrg.medium.com/build-a-web-app-using-pythons-flask-for-beginners-f28315256893
# https://stackoverflow.com/questions/42465768/jinja2-template-not-found-and-internal-server-error

import server
import auth
from django.shortcuts import redirect

import flask
from flask import Flask, request, render_template, jsonify, redirect, url_for

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
        return
        
    if server.check_user(username) == -1:
        return flask.render_template('create_account.html')
    else:
        # fix url
        return redirect('/dashboard')
        
@app.route('/profile')
def profile():
    username = auth.authenticate()
    if server.check_user(username) == -1:
        return redirect('/create')
    details = server.profile_details(username)
    name = details[0][1]
    year = details[0][3]
    plan = details[0][4]
    number = details[1][1]
    return flask.render_template('profile_page.html', name = name, netid = str(username), class_year = year, dining_plan = plan, phone_no = number)

@app.route('/updatedetails', methods = ['GET', 'POST'])
def update_details():
    username = auth.authenticate()
    if flask.request.method == 'POST':
        server.update_details(flask.request.form, username)
        return 

    if server.check_user(username) != -1:
        return flask.render_template('update_details.html')       
    else: 
        return redirect('/create')




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
        return redirect('/create')

@app.route('/yourrequests')
def your_requests():
    username = auth.authenticate()
    req_table = server.get_your_requests(username)
    
    return flask.render_template('your_requests.html', table= req_table)

@app.route('/submitrequest', methods = ['GET', 'POST'])
def submit_request():
    username = auth.authenticate()

    if flask.request.method == 'POST':
        server.create_request(flask.request.form, username)
        return 

    if server.check_user(username) != -1:
        return flask.render_template('submitrequest.html')       
    else: 
        return redirect('/create')
    
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
        return redirect('/about')
    
    return flask.render_template('viewrequest.html', req=req)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

