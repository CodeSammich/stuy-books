from flask import Flask, render_template, url_for, session, request
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
        print 'hello'
        return render_template("login.html")
    else:
        print request.form
        email = request.form['email']
        pword = request.form['pword']
        print email
        print pword

        m = sha256()
        m.update(pword)
        passwordHash = m.hexdigest()

        if authenticate(email, passwordHash):
            session['email'] = email
            return redirect(url_for("home"))
        else:
            return render_template('login.html', msg = 'Incorrect email/password combination')

@app.route("/signup")
def signup():
    if request.method == "GET":
        print request
        return render_template("signup.html")
    else:
        email = request.form['email']
        pword = request.form['pword']
        first = request.form['first']
        last = request.form['last']
        confirm = request.form['confirm']

        if email == '':
            return render_template('signup.html', msg = 'Please enter your stuy.edu email')
        if len(pword) < 8:
            return render_template('signup.html', msg = 'Please enter a password that is at least 8 characters long')
        if pword != confirm:
            return render_template('signup.html', msg = 'Password does not match the confirm password')

        m = sha256()
        m.update(pword)
        passwordHash = m.hexdigest()

        message = addUser(email, passwordHash, first, last)

        if (message == ''):
            return redirect(url_for('home'))
        return render_template('signup.html', msg = message)

if __name__ == "__main__":
    app.debug = True
    app.run('0.0.0.0',port=8000)
