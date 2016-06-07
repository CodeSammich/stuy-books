from flask import Flask, render_template, url_for, session, request, redirect
from database import *
from functools import wraps
from hashlib import sha256
from uuid import uuid4
from urllib import urlencode
from email.mime.multipart import MIMEMultipart
from email.MIMEText import MIMEText
from os import urandom
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
        if request.args.get('name') != None:
            #Why does it automatically use Google Sign in without me pressing bttn
            name = request.args.get('name')
            email = request.args.get('email')

            #strip the @stuy.edu part
            email = email[:-9]
            session['email'] = email
            print "boo**********\n"
            return render_template("index.html")
        #elif "email" in session:
            #return redirect(url_for("userpage"))
        else:
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

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'GET':
        return render_template('forgot.html')
    else:

        email = request.form.get('email')
        if email == None:
            return render_template('forgot.html', msg = 'You must enter your email!')
        if getUser(email) == None:
            return render_template('forgot.html', msg = 'That is an invalid email!')

        randomGen = urandom(64).encode('base-64') #just for something random
        setReset(email, randomGen)

        data = urlencode(randomGen)
        link = 'http://localhost:8000/change?reset=%s' %(data)

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(ourEmail, ourPassword)

        #Sending the seller an email
        message = MIMEMultipart('alternative')
        message['Subject'] = 'Reset password'
        message['From'] = ourEmail
        message['To'] = email

        text = '''Hello,\n\nYou indicated that you have forgotten your password.\nClick on this link to reset your password: %s\n\nYours,\nTeam JASH''' %(email, link)
        html = '''
        <html>
            <body>
                <p>Hello,<br><br>
                You indicated that you have forgotten your password.<br>
                <a href=%s>Click to reset</a> <br><br>
                Yours,<br>
                Team JASH
        ''' %(link)

        textcomp = MIMEText(text, 'plain')
        htmlcomp = MIMEText(html, 'html')
        message.attach(textcomp)
        message.attach(htmlcomp)
        s.sendmail(ourEmail, email, message.as_string())
        s.close()

        return redirect(url_for('home'))

@app.route('/change', methods=['GET', 'POST'])
def change():
    code = request.args.get('reset')
    if request.method == 'GET':
        if code == None:
            return redirect(url_for('login')) #They are not allowed to access the page directly
        return render_template('change.html')
    else:
        email = getEmailFromReset(code)
        pword = request.form.get('pword')
        confirm = request.form.get('confirmpword')
        if len(pword) < 8:
            return render_template('change.html', msg='Your password must be at least 8 characters long!', reset=code )
        if len(confirmpword) < 8:
            return render_template('change.html', msg2='The confirm password must be at least 8 characters long!', reset=code )
        if pword != confirmpword:
            return render_template('change.html', msg='The confirm password must match the password!', reset=code )
        hasReset(code) #sets to reset code back to ''

        m = sha256()
        m.update(pword)
        passwordHash = m.hexdigest()

        updatePassword(email, passwordHash)
        return redirect(url_for('login'))

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
        i = 0
        available=[]
        pending=[]
        sold=[]
        while i < len(info):
            if info[i]["status"] == "available":
                available.append(info[i])
            elif info[i]["status"] == "pending":
                pending.append(info[i])
            else:
                sold.append(info[i])
            i+=1
        print available
        return render_template("userpage.html", info=info, available=available, pending=pending, sold=sold)
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
        info = listAll()
        actualones = []
        for i in range(len(info)):
            if info[i].get('status', None) == 'available':
                actualones.append(info[i])
        return render_template('buypage.html', info=actualones)
    else:
        search = request.form['searchQuery']
        #print search
        #results = searchForBook(search)
        #print results
        #session['results'] = results
        #return render_template("search.html", info=results)
        return redirect(url_for('search', query=search))


@app.route("/itempage/<email>/<bookName>/<author>/<price>/<condition>", methods=['GET','POST'])
@requireLogin
def itempage(email, bookName, author, price, condition):
    if request.method == "GET":
        info = listAll()
        for i in range(len(info)):
            if email == info[i]['email'] and bookName == info[i]['bookName'] and author == info[i]['author'] and price == info[i]['price'] and condition == info[i]['condition']:
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

@app.route('/edit/<bookName>', methods=['GET', 'POST'])
@requireLogin
def edit(bookName):
    if request.method == 'GET':
        bookName = bookName.replace("%20", " ")
        print bookName
        email = session['email']
        bookInfo = getBookInfo(bookName, email)
        print bookInfo
        if bookInfo == None:
            return redirect(url_for('userpage'), msg = 'You can only edit a book that you own.')
        return render_template('edit.html', bookInfo=bookInfo)
    else:
        email = session['email']
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['serial']
        subject = request.form['subject']
        condition = request.form['condition']
        price = request.form['price']

        updateBookInfo(bookName ,email, title, author, isbn, subject, condition, price)
        #return render_template('edit.html')
        return redirect(url_for('userpage'))


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
        #return render_template("search.html", info=results)getBookInfogetBookInfo
        return redirect(url_for('search', query=search))
    else:
        search = request.args.get("query")
        results = searchForBook(search)
        return render_template("search.html", info=results)

@app.route('/finish/<email>/<bookName>/<author>/<price>/<condition>')
@requireLogin
def finish(email, bookName, author, price, condition):
    print 'Begin email to both parties to indicate finished transaction'
    bookName = bookName.replace("%20", " ")

    sellerEmail = email + '@stuy.edu'
    buyerEmail = getBuyerEmail(email, bookName, author, price, condition) + '@stuy.edu'

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(ourEmail, ourPassword)

    messageS = MIMEMultipart()
    messageS['Subject'] = 'Finished transaction'
    messageS['From'] = ourEmail
    messageS['To'] = sellerEmail

    textS = '''
    Hello,

    You have confirmed that yours transaction for %s has been successful.
    If you did not confirm this, contact us immediately at %s

    Yours,
    Team JASH''' %(bookName, ourEmail)


    messageS.attach(MIMEText(textS, 'plain'))
    s.sendmail(ourEmail, sellerEmail, messageS.as_string())

    messageB = MIMEMultipart()
    messageB['Subject'] = 'Finished transaction'
    messageB['From'] = ourEmail
    messageB['To'] = buyerEmail

    textB = '''
    Hello,

    Our records indicate that you have bought %s for %s. The seller has confirmed that have received the book.
    If you have not received your book contact us immediately at %s

    Yours,
    Team JASH''' %(bookName, price, ourEmail)

    messageS.attach(MIMEText(textB, 'plain'))
    s.sendmail(ourEmail, buyerEmail, messageB.as_string())

    s.close()

    setBookStatus(bookName, email, author, price, condition, 'sold')
    setBuyerEmail(bookName, email, author, price, condition, '')

    return redirect(url_for('userpage'))

@app.route('/bought/<email>/<bookName>/<author>/<price>/<condition>', methods=['GET', 'POST'])
@requireLogin
def bought(email, bookName, author, price, condition):
    print 'HELLO THIS IS IN THE BOUGHT SECTION'

    sellerEmail = email + '@stuy.edu'
    buyerEmail = session['email'] + '@stuy.edu'

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
    Team JASH''' %(bookName, price, buyerEmail)

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
    Team JASH''' %(bookName, price, sellerEmail)

    messageB.attach(MIMEText(textB, 'plain'))
    s.sendmail(ourEmail, buyerEmail, messageB.as_string())

    s.close()

    setBookStatus(bookName, email, author, price, condition, 'pending')
    setBuyerEmail(bookName, email, author, price, condition, session['email'])

    return redirect(url_for('userpage'))

@app.route('/cancel/<email>/<bookName>/<author>/<price>/<condition>')
@requireLogin
def cancel(email, bookName, author, price, condition):
    bookName = bookName.replace('%20', ' ')
    author = author.replace('%20', ' ')
    setBookStatus(bookName, session['email'], author, price, condition, 'available')
    setBuyerEmail(bookName, session['email'], author, price, condition, '')

    #Alert the buyer that the seller has canceled the transaction
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(ourEmail, ourPassword)

    message = MIMEMultipart()
    message['Subject'] = 'Transaction canceled'
    message['From'] = ourEmail
    message['To'] = session['email'] + '@stuy.edu'

    text = '''
    To whom it may concern,

    You indicated that you wanted %s for $%s. The seller has canceled this transaction.
    If this is a mistake you can contact the seller at %s.

    Yours,
    Team JASH''' %(bookName, price, email + '@stuy.edu')

    message.attach(MIMEText(text, 'plain'))
    s.sendmail(ourEmail, session['email'] + '@stuy.edu', message.as_string())

    s.close()

    setBookStatus(bookName, email, author, price, condition, 'available')
    setBuyerEmail(bookName, email, author, price, condition, session['email'])
    return redirect(url_for('userpage'))

@app.route('/remove/<email>/<bookName>/<author>/<price>/<condition>')
@requireLogin
def remove(email, bookName, author, price, condition):
    bookName = bookName.replace("%20", " ")
    author = author.replace('%20', ' ')
    deleteAllBooks(email, bookName, author, price, condition)
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
