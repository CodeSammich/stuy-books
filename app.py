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

"""
def requireLogin(f):
    @wraps(f)
    def dec(*args):
        if session('email') is not None:
            return f(*args)
        else:

            return render_template('login.html', msg = 'You must login to view the page')
    return dec
"""

def requireLogin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('email') is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=["GET","POST"])
@app.route('/index', methods=["GET","POST"])
@app.route("/home/", methods=["GET","POST"])
def home():
    if request.method == "GET":
        return render_template("index.html")
    else:
        search = request.form['searchQuery']
        #print search
        #results = searchForBook(search)
        #print results
        #session['results'] = results
        #return render_template("search.html", info=results)
        return redirect(url_for('search', query=search))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        if request.args.get('name') != None:
            #Why does it automatically use Google Sign in without me pressing bttn
            name = request.args.get('name')
            email = request.args.get('email')

            #strip the @stuy.edu part
            email = email[:-9]
            session['email'] = email
            print "boo**********\n"
            return redirect(url_for("userpage", email=email))
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
            session['email'] = email
            return redirect(request.args.get('next', url_for('userpage', email=email)))

        return render_template('login.html', msg = 'Incorrect email/password combination')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
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
            #print message.as_string()

            s.sendmail(ourEmail, email + '@stuy.edu', message.as_string())
            s.close()

            return redirect(url_for('home'))

        return render_template('signup.html', msg = message)

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
@requireLogin
def userpage():
    if request.method == "GET":
        email = session.get('email', None)
        #if email == None:
            #return redirect(url_for('login'), msg = 'You must log in first!')
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
@requireLogin
def sell():
    if request.method == 'GET':
        return render_template('sell.html')
    else:
        #TODO make the form save and add required fields
        #form = request.form
        email = session['email']
        bookName = request.form['title']
        author = request.form['author']
        isbn = request.form['serial']
        subject = request.form['subject']
        condition = request.form['condition']
        price = request.form['price']

        is_new = addBook(email, bookName, author, isbn, subject, condition, price)

        if is_new:
            return redirect(url_for('userpage'))
        else:
            return render_template('sell.html', msg="Book already exists")

@app.route('/buypage', methods=['GET', 'POST'])
@requireLogin
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
@requireLogin
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

@app.route('/edit', methods=['GET', 'POST'])
@requireLogin
def edit():
    if request.method == 'GET':
        return render_template('edit.html')
    #TODO check if user is logged in, same thing for sell page
    email = session['email']
    bookName = request.form['title']
    author = request.form['author']
    isbn = request.form['serial']
    subject = request.form['subject']
    condition = request.form['condition']
    price = request.form['price']

    updateBookInfo(email, bookName, author, isbn, subject, condition, price)
    return render_template('edit.html')

'''
def autocomplete():
@app.route('/search', methods=['GET','POST'])
'''

@app.route('/search', methods=["GET","POST"])
@requireLogin
def search():
    if request.method=="POST":
        search = request.form['searchQuery']
        #print search
        #results = searchForBook(search)
        #print results
        #session['results'] = results
        #return render_template("search.html", info=results)
        return redirect(url_for('search', query=search))
    else:
        search = request.args.get("query")
        results = searchForBook(search)
        return render_template("search.html", info=results)

@app.route('/finish', methods=['GET', 'POST'])
@requireLogin
def finish():
    print 'Begin email to both parties to indicate finished transaction'

    sellerEmail = session['email'] + '@stuy.edu'
    if request.method == 'GET':
        return render_template('userpage.html', message = '')
    else:
        return redirect(url_for('userpage'), render=True)

@app.route('/bought', methods=['GET', 'POST'])
def bought():
    print 'HELLO THIS IS IN THE BOUGHT SECTION'

    sellerEmail = request.args.get('email') + '@stuy.edu'
    buyerEmail = session['email'] + '@stuy.edu'
    book = request.args.get('bookName')
    price = request.args.get('price')

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(ourEmail, ourPassword)

    #Sending the seller an email
    messageS = MIMEMultipart()
    messageS['Subject'] = 'Someone is interested in your book'
    messageS['From'] = ourEmail
    messageS['To'] = sellerEmail

    textS = '''
    To whom it may concern,

    You have listed the book %s for sale for $%s. We are pleased to say that
    someone has seen the offer and will gladly meet up with you to purchase the book.
    You can reach the buyer at %s

    Yours,
    Team JASH''' %(book, price, buyerEmail)

    messageS.attach(MIMEText(textS, 'plain'))
    s.sendmail(ourEmail, sellerEmail, messageS.as_string())

    #Sending the buyer an email
    messageB = MIMEMultipart()
    messageB['Subject'] = 'You have shown interest for a book'
    messageB['From'] = ourEmail
    messageB['To'] = buyerEmail

    textB = '''
    To whom it may concern,

    You have indicated that you want to buy the book %s for $%s.
    You can contact the seller at %s

    Yours,
    Team JASH''' %(book, price, sellerEmail)

    messageB.attach(MIMEText(textB, 'plain'))
    s.sendmail(ourEmail, buyerEmail, messageB.as_string())

    s.close()

    setBookStatus(book, request.args.get('email'), 'pending')

    return redirect(url_for('userpage'))

@app.route('/googleLogin')
def googleLogin():
    if request.method=="GET":
        print "hello"
        name = request.args.get('name')
        print name
        email = request.args.get('email')
        print email
        session['email'] = email
        print "boo\n***********"
        return redirect(url_for('home'))#url_for("userpage", email=email))
    else:
        return render_template("google.html")

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.secret_key = str(uuid4())
    app.debug = True
    app.run('0.0.0.0',port=8000)
