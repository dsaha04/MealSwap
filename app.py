# https://pemagrg.medium.com/build-a-web-app-using-pythons-flask-for-beginners-f28315256893
# https://stackoverflow.com/questions/42465768/jinja2-template-not-found-and-internal-server-error

from flask import Flask, request, render_template, jsonify, redirect, url_for

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/create')
def create():
    return render_template('create_account.html')


@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/create-new-user', methods=['GET', 'POST'])
def my_form_post():
    if request.method == 'POST':
        firstname = request.form['firstname']

        result = {
            "output": firstname
        }

        server.create_user(request.form)
        
        # TODO: ADD TO DATABASE HERE
        
        # TODO; Redirect the user instead of calling jsonify
        
        return jsonify(result=result)

    return render_template('create_account.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
