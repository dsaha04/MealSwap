# https://pemagrg.medium.com/build-a-web-app-using-pythons-flask-for-beginners-f28315256893
# https://stackoverflow.com/questions/42465768/jinja2-template-not-found-and-internal-server-error

import server
import auth

from flask import Flask, request, render_template, jsonify, redirect, url_for

app = Flask(__name__)

app.secret_key = '1234'


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/create', methods = ['GET', 'POST'])
def create():
    username = auth.authenticate()
    if server.check_user(username) == -1:
        if request.method == 'POST':
            server.create_user(request.form, username)
        return render_template('create_account.html')
    else: 
        return render_template('dashboard.html')
        
@app.route('/profile')
def profile():
    username = auth.authenticate()
    if server.check_user(username) == -1:
        return create()
    details = server.profile_details(username)
    name = details[0][1]
    year = details[0][3]
    plan = details[0][4]
    number = details[1][1]
    return render_template('profile_page.html', name = name, netid = str(username), class_year = year, dining_plan = plan, phone_no = number)

@app.route('/test')
def test():
    return render_template('test.html')

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
    return render_template('about.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/submitrequest', methods = ['GET', 'POST'])
def submit_request():
    username = auth.authenticate()

    if request.method == 'POST':
        server.create_request(request.form, username)
        return 

    if server.check_user(username) != -1:
        return render_template('submitrequest.html')       
    else: 
        return create()



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

