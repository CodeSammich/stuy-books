from flask import Flask, render_template, url_for, session, request, redirect
from database import *
from functools import wraps
from hashlib import sha256
from smtplib import SMTP #TODO
from uuid import uuid4

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
    session["logged"]=0
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    session["logged"]=0
    if request.method == "GET":
        return render_template("login.html")
    else:
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
            session['logged'] = 1
            return redirect(url_for("userpage", email=email))
        else:
            return render_template('login.html', msg = 'Incorrect email/password combination')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    session["logged"]=0
    if request.method == "GET":
        return render_template("signup.html")
    else:
        email = request.form['email']
        pword = request.form['pword']

        if email == '':
            return render_template('signup.html', msg = 'Please enter your stuy.edu email')
        if len(pword) < 8:
            return render_template('signup.html', msg = 'Please enter a password that is at least 8 characters long')
        #if pword != confirm:
            #return render_template('signup.html', msg = 'Password does not match the confirm password')
        m = sha256()
        m.update(pword)
        passwordHash = m.hexdigest()

        message = addUser(email, passwordHash)
        if (message == ''):
            return redirect(url_for('home'))
        return render_template('signup.html', msg = message)

@app.route("/userpage")
@requireLogin
def userpage():
    if request.method == "GET":
        return render_template("userpage.html")
    return redirect(url_for('sell'))

@app.route('/sell')
def sell():
    return render_template('sell.html')

@app.route('/logout')
@requireLogin
def logout():
    del session['email']
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.secret_key = str(uuid4())
    app.debug = True
    app.run('0.0.0.0',port=8000)
