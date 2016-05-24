from flask import Flask, render_template, url_for, session, request, redirect
from database import *
from functools import wraps
from hashlib import sha256
from smtplib import SMTP #TODO
from uuid import uuid4

app = Flask(__name__)

ourEmail = 'stuybooks.JASH@gmail.com'
ourPassword = open('password.txt', 'r').read()[:-1]

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
    session['logged'] == 0
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
            print 'hello sir'
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
            """
            data = urllib.urlencode({'email': email, 'passwordHash': passwordHash})
            activateLink = 'localhost:8000/activate?%s' %(data)

            s = SMTP('smpt.gmail.com' 587)
            s.startls()
            s.ehlo()
            s.login(ourEmail, ourPassword)

            messge = '''To: %s
            From: %s
            Subject: Getting Started with StuyBooks

            Dear %s,

            Thanks for signing up with StuyBooks!
            Click on this link to activate your account: %s
            If you did not register for StuyBooks, contact us at %s

            Sincerely,
            Team JASH''' %(email + '@stuy.edu', ourEmail, name, activateLink ,ourEmail)
            s.sendmail(ourEmail, sellerEmail, message)
            s.close()
            """
            return redirect(url_for('home'))
        return render_template('signup.html', msg = message)

@app.route('/activate')
def activate():
    return render_template('activate.html')

@app.route("/userpage", methods=['GET', 'POST'])
def userpage():
    if request.method == "GET":
        email = session['email']
        info = listBooksForUser(email)
        return render_template("userpage.html", info=info)
    return redirect(url_for('sell'))

@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'GET':
        return render_template('sell.html')
    else:
        email = session['email']
        bookName = request.form['title']
        author = request.form['author']
        isbn = request.form['serial']
        subject = request.form['subject']
        condition = request.form['condition']
        price = request.form['price']
        description = request.form['comment']

        addBook(email, bookName, author, isbn, subject, condition, price, description)

        return redirect(url_for('userpage'))

@app.route('/buypage')
def buy():
    return render_template('buypage.html', info=listAll())

@app.route('/googleLogin')
def googleLogin():
    if request.method=="GET":
        print "hello"
        name = request.args.get('name')
        print name
        email = request.args.get('email')
        print email
        session['email'] = email
        session['logged'] = 1
        print session['email']
        print session['logged']
        return redirect(url_for("userpage", email=email))
    else:
        return render_template("google.html")

@app.route('/logout')
@requireLogin
def logout():
    del session['email']
    return redirect(url_for(''))

if __name__ == "__main__":
    app.secret_key = str(uuid4())
    app.debug = True
    app.run('0.0.0.0',port=8000)
