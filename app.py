from flask import Flask, render_template, url_for, session, request, redirect
from database import *
from functools import wraps
from hashlib import sha256
from uuid import uuid4
from urllib import urlencode
from email.mime.multipart import MIMEMultipart
from email.MIMEText import MIMEText
import smtplib

app = Flask(__name__)

ourEmail = 'stuybooks.JASH@gmail.com'
ourPassword = open('password.txt', 'r').read()[:-1]

#def requireLogin(f):
#    @wraps(f)
#    def dec(*args):
#        if 'email' not in session:
#            return render_template('login.html', msg = 'You must login to view the page')
#        return f(*args)
#    return dec

@app.route('/', methods=["GET","POST"])
@app.route('/index', methods=["GET","POST"])
@app.route("/home/", methods=["GET","POST"])
def home():
    session["logged"]=0
    if request.method == "GET":
        return render_template("index.html")
    else:
        print "hi123"
        search = request.form['searchQuery']
        #print search
        #results = searchForBook(search)
        #print results
        #session['results'] = results
        #return render_template("search.html", info=results)
        return redirect(url_for('search', query=search))



@app.route("/login", methods=["GET","POST"])
def login():
    session['logged'] == 0
    if request.method == "GET":
        if request.args.get('name') != None:
            name = request.args.get('name')
            print name
            email = request.args.get('email')
            print email

            #strip the @stuy.edu part
            #email = email[:-9]
            #

            session['email'] = email
            session['logged'] = 1
            print session['email']
            print session['logged']
            return redirect(url_for("userpage"))
        else:
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

            user = getUser(email)
            data = urlencode({'email': user['email'], '_id': user['_id']})
            activateLink = 'http://localhost:8000/activate?%s' %(data)

            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(ourEmail, ourPassword)

            #Sets up the multipart object
            message = MIMEMultipart()
            message['Subject'] = 'Getting started with StuyBooks'
            message['From'] = ourEmail
            message['To'] = email + '@stuy.edu'

            text = '''
            To whom it may concern,

            Thanks for signing up with StuyBooks!
            Click on this link to activate your account: %s
            If you did not register for StuyBooks, contact us at %s

            Sincerely,
            Team JASH''' %(activateLink , ourEmail)
            #Attaches the message
            message.attach(MIMEText(text, 'plain'))
            print message.as_string()

            s.sendmail(ourEmail, email + '@stuy.edu', message.as_string())
            s.close()

            return redirect(url_for('home'))

        return render_template('signup.html', msg = message)

#TODO
@app.route('/activate', methods=['GET', 'POST'])
def activate():
    if request.method == 'GET':
        email = request.args['email']
        if getStatus(email):
            return redirect(url_for('home'))
        updateStatus(email)
        print getStatus(email)
        return render_template('activate.html')
    return redirect(url_for('home'))

@app.route("/userpage", methods=['GET', 'POST'])
def userpage():
    if request.method == "GET":
        email = session['email']
        info = listBooksForUser(email)
        return render_template("userpage.html", info=info)
    else:
        print "hello"
        search = request.form['searchQuery']
        #print search
        #results = searchForBook(search)
        #print results
        #session['results'] = results
        #return render_template("search.html", info=results)
        return redirect(url_for('search', query=search))
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

        addBook(email, bookName, author, isbn, subject, condition, price)

        return redirect(url_for('userpage'))

@app.route('/buypage', methods=['GET', 'POST'])
def buy():
    if request.method == "GET":
        return render_template('buypage.html', info=listAll())
    else:
        search = request.form['searchQuery']
        #print search
        #results = searchForBook(search)
        #print results
        #session['results'] = results
        #return render_template("search.html", info=results)
        return redirect(url_for('search', query=search))


@app.route("/itempage/<email>/<bookName>", methods=['GET','POST'])
def itempage(email, bookName):
    if request.method == "GET":
        info = listAll()
        for i in range(len(info)):
            if email == info[i]['email'] and bookName == info[i]['bookName']:
                thisBook = info[i]
                return render_template("itempage.html", thisBook=thisBook)
    else:
        search = request.form['searchQuery']
        #print search
        #results = searchForBook(search)
        #print results
        #session['results'] = results
        #return render_template("search.html", info=results)
        return redirect(url_for('search', query=search))


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search = request.args.get("query")
        results = searchForBook(search)
        return render_template("search.html", info=results)
    return render_template('search.html')

def autocomplete():


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
def logout():
    del session['email']
    session['logged'] = 0
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.secret_key = str(uuid4())
    app.debug = True
    app.run('0.0.0.0',port=8000)
