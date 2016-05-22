from flask import Flask, render_template, url_for, session, request
from database import *
from functools import wraps
from hashlib import sha256
from smtplib import SMTP #TODO

app = Flask(__name__)

def requireLogin(f):
    @wraps(f)
    def dec(*args):
        if 'email' not in session:
            return render_template('login.html', msg = 'You must login to view the page')
        return f(*args)
    return dec

@app.route('/')
@app.route('/index')
@app.route("/home/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        print request.form
        email = request.form['email']
        pword = request.form['pword']

        if email == '':
            return render_template('login.html', msg = 'Please enter your email')
        if pword == '':
            return render_template('login.html', msg = 'Please enter your password')

        m = sha256()
        m.update(pword)
        passwordHash = m.hexdigest()

        if authenticate(email, passwordHash):
            session['email'] = email
            return redirect(url_for("home"))
        else:
            return render_template('login.html', msg = 'Incorrect email/password combination')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        email = request.form['email']
        pword = request.form['pword']
        print 'hello'

        if email == '':
            return render_template('signup.html', msg = 'Please enter your stuy.edu email')
        if len(pword) < 8:
            return render_template('signup.html', msg = 'Please enter a password that is at least 8 characters long')
        #if pword != confirm:
            #return render_template('signup.html', msg = 'Password does not match the confirm password')
        print 'hello2'
        m = sha256()
        m.update(pword)
        passwordHash = m.hexdigest()

        message = addUser(email, passwordHash)
        print message
        if (message == ''):
            return redirect(url_for('home'))
        return render_template('signup.html', msg = message)

if __name__ == "__main__":
    app.debug = True
    app.run('0.0.0.0',port=8000)
