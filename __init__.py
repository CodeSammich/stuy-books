'''
Authors: Amanda Chiu, Helen Li, Samuel Zhang, Jeffrey Zou
Description: Middleware Flask Application with Gmail SMTP integration

------------------------------------
Standard flask application, no specific design notes needed.

------------------------------------
For database design notes, please see 'database.py'
For ranking design notes, please see 'ranking.py'
For image design notes, please see 'image.py'

------------------------------------

Please note: In documentation:
   - All variable names are denoted with single apostrophes ( ' )
   - All string values are denoted with double apostrophes ( " )
   - All relevant information under a particularly heading are denoted with ( - )
   - All important caveats are denoted with ( NOTE )

*** -----  SYSTEM ADMINISTRATORS PLEASE SEE BELOW  ------- ***

'''

from flask import Flask, render_template, url_for, session, request, redirect
from functools import wraps
from hashlib import sha256
from uuid import uuid4
from urllib import urlencode
from email.mime.multipart import MIMEMultipart
from email.MIMEText import MIMEText
import os
import smtplib
from raven.contrib.flask import Sentry
# sentry = Sentry(app, dsn='YOUR_DSN_HERE')


# integrate other files
import database
import ranking
import image

app = Flask(__name__)

''' ------------------- SYSTEM ADMIN AREA BEGIN --------------------- '''

'''
SYSTEM MANAGEMENT ADMINISTRATION VARIABLES: VARIES DEPENDING ON DEPLOYMENT

Change 'website_url' if using new domain / I.P. Address

Change 'home_dir' to either '' or '' + os.path.dirname(__file) + '/'
    - Whichever works is fine, may vary depending on deployment distro

Change 'password_dir' to os.path.dirname(__file__) with or without " + '/' "
    - Certain Apache2 servers require the trailing forward slash
    - Check Apache2 error logs for reference

Change 'ourEmail' in case company / devteam email changes
    - NOTE: Only guaranteed to work with Gmail servers
    - Use other email addresses at your own risk

Change 'ourPassword' ONLY if:
  - Directory for 'password.txt' changes as a last resort
  - Directory should be able to change by just editing 'password_dir'; see above
    - NOTE: This is a private file and is NOT pushed on Github
    - Required in order to run "stuy-books" web application

  NOTE: Change 'password.txt' ONLY if 'ourEmail' changes
    - 'ourPassword' is the password to 'ourEmail'
    - Password must be stored in a file named 'password.txt'
        - NOTE: 'password.txt' MUST have a trailing '\n' or new line character in file

Change 'siteAdmin' and 'siteAdminEmailService' if:
    - Admin email changes

NOTE: As of 7/20/16, stuy-books only accepts @stuy.edu emails for administrators

'''
# hosted at NameCheap from Github Student Pack until 7/10/2017
#website_url = 'http://www.stuybooks.me'
website_url = 'localhost:5000' # change back to url once done

# base directory for stuy-books
home_dir = "" #+ os.path.dirname(__file__) + '/'

# Use only with local machines when testing
password_dir = os.path.dirname(__file__)

# Use only with Apache2 Server (Epsilon)
#password_dir = os.path.dirname(__file__) + '/'

ourEmail = 'stuybooks.JASH@gmail.com'
ourPassword = open( password_dir + 'password.txt', 'r').read()[:-1]

# NOTE: As of 7/20/16, stuy-books only accepts @stuy.edu emails for administrators

siteAdmin = 'helen1@stuy.edu'
siteAdminEmailService = '@stuy.edu'

''' ---------------- SYSTEM ADMIN AREA END ------------------- '''

#Wrapper function put before routes that require user to log in
def requireLogin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('email') is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def requireAdmin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print session.get('email')
        if session.get('email') + siteAdminEmailService != siteAdmin:
            return redirect(url_for('home', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=["GET","POST"])
@app.route('/index', methods=["GET","POST"])
@app.route("/home", methods=["GET","POST"])
def home():
    if request.method == "GET":
        if request.args.get('name') != None:
            #Why does it automatically use Google Sign in without me pressing bttn
            name = request.args.get('name')
            email = request.args.get('email')

            if email[-9:] == "@stuy.edu":
                #strip the @stuy.edu part
                email = email[:-9]
                session['email'] = email

                return render_template("index.html")
            else:
                return redirect(url_for('login', msg="Email is not valid. Please use a stuy.edu email."))
        else:
#            path = path.dirname("index.html")
#            print path
            return render_template("index.html")
    else:
        search = request.form['searchQuery']
        return redirect(url_for('search', query=search))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        if request.args.get("msg") == None:
            return render_template("login.html")
        else:
            msg=request.args.get("msg")
            return render_template("login.html", msg=msg)
    else:
        email = request.form['email']
        pword = request.form['pword']

        if email == '':
            return render_template("login.html", msg = 'Please enter your email')
        if pword == '':
            return render_template("login.html", msg = 'Please enter your password')

        m = sha256()
        m.update(pword)
        passwordHash = m.hexdigest()

        if database.authenticate(email, passwordHash):
            session['email'] = email
            if session['email'] + siteAdminEmailService == siteAdmin:
                # Site admins may not have "@stuy.edu" emails
                session['email'] = email # + siteAdminEmailService
                return redirect(url_for('admin'))
            # request.args.get'next') ==> doesn't redirect to home, but last active page
            return redirect(request.args.get('next') or url_for('home')) #redirect still internal server error

        return render_template("login.html", msg = 'Incorrect email/password combination. If you have not activated your account, please check your email for an activation link.')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        email = request.form['email']
        pword = request.form['pword']

        if email == '' or email.find('@') != -1:
            return render_template("signup.html", msg = 'Please enter your stuy.edu email')
        if len(pword) < 8:
            return render_template("signup.html", msg = 'Please enter a password that is at least 8 characters long')
        m = sha256()
        m.update(pword)
        passwordHash = m.hexdigest()

        print "password hashed"

        message = database.addUser(email, passwordHash)

        print "user added to database"
        if (message == ''):
            user = database.getUser(email)
            data = urlencode({'email': user['email'], '_id': user['_id']})
            activateLink = website_url + '/activate?%s' %(data)

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
            Hello,

            Thanks for signing up with StuyBooks!
            Click on this link to activate your account: %s
            If you did not register for StuyBooks, contact us at %s

            Disclaimer: Stuy-books is a platform to meet and trade with other students. Stuy-books and associates are not liable for any damages, infringements, or other inappropriate usage of our service. Please be respectful of others. Any violation of school regulation can and will be reported to the administration. Thank you.

            Sincerely,
            Team JASH''' %(activateLink , ourEmail)
            #Attaches the message
            message.attach(MIMEText(text, 'plain'))

            s.sendmail(ourEmail, email + '@stuy.edu', message.as_string())
            s.close()

            return render_template("signup.html", msg = "A confirmation email has been sent to " + email + '@stuy.edu')

        return render_template("signup.html", msg = message)

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'GET':
        return render_template("forgot.html")
    else:

        email = request.form.get('email')
        if email == None:
            return render_template("forgot.html", msg = 'You must enter your email!')
        if database.getUser(email) == None:
            return render_template("forgot.html", msg = 'That is an invalid email!')

        randomGen = os.urandom(64).encode('base-64') #just for something random
        database.setReset(email, randomGen)

        data = urlencode(randomGen)
        link = website_url + '/change?reset=%s' %(data)

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
        return render_template("change.html")
    else:
        email = database.getEmailFromReset(code)
        pword = request.form.get('pword')
        confirm = request.form.get('confirmpword')
        if len(pword) < 8:
            return render_template("change.html", msg='Your password must be at least 8 characters long!', reset=code )
        if len(confirmpword) < 8:
            return render_template("change.html", msg2='The confirm password must be at least 8 characters long!', reset=code )
        if pword != confirmpword:
            return render_template("change.html", msg='The confirm password must match the password!', reset=code )
        database.hasReset(code) #sets to reset code back to ''

        m = sha256()
        m.update(pword)
        passwordHash = m.hexdigest()

        database.updatePassword(email, passwordHash)
        return redirect(url_for('login'))

@app.route('/activate', methods=['GET', 'POST'])
def activate():
    if request.method == 'GET':
        email = request.args['email']
        if database.getStatus(email):
            return redirect(url_for('home'))
        database.updateStatus(email)
        return render_template("activate.html")
    return redirect(url_for('home'))

@app.route("/userpage", methods=['GET', 'POST'])
@requireLogin
def userpage():
    if request.method == "GET":
        email = session.get('email', None)
        print email
#        print email
        if email != siteAdmin:
            info = database.listBooksForUser(email)
            bought = database.listBoughtForUser(email)

            #for boughtBook in bought:
            #    bookName = boughtBook['bookName']
            #    author = boughtBook['author']
            #    if database.getBookRating(bookName,author)
            #getBookRating(email, bookName, author, price, condition)

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
            return render_template("userpage.html", info=info, available=available, pending=pending, sold=sold, bought=bought, admin=False, email=email)
        else:
            return redirect(url_for('admin'))

    else:
        search = request.form['searchQuery']
        return redirect(url_for('search', query=search))
    return redirect(url_for('sell'))

@app.route('/sell', methods=['GET', 'POST'])
@requireLogin
def sell():
    if request.method == 'GET':
        return render_template("sell.html")
    else:
        if request.form['signup'] == "sell":
            email = session['email']
            bookName = request.form['title']
            author = request.form['author']
            isbn = request.form['serial']
            subject = request.form['subject']
            condition = request.form['condition']
            price = request.form['price']

            is_new = database.addBook(email, bookName, author, isbn, subject, condition, price)

            if is_new:
                return redirect(url_for('userpage'))
            else:
                return render_template("sell2.html", bookName=bookName, author=author, isbn=isbn, subject=subject, condition=condition, price=price, msg="Book already exists")
        elif request.form['signup'] == "search":
            search = request.form['searchQuery']
        return redirect(url_for('search', query=search))

@app.route('/buypage', methods=['GET', 'POST'])
@requireLogin
def buy():
    if request.method == "GET":
        info = database.listAll()
        actualones = []
        ratings = []
        for i in range(len(info)):
            if info[i].get('status', None) == 'available':
                sellerEmail = info[i]['email']

                # remove @stuy.edu (intended for admin email)
                sellerEmail = sellerEmail.replace( siteAdminEmailService, '' )

                rating = database.getUserRating(sellerEmail)
                info[i]['rating'] = rating
                print "info rating:"
                print info[i]['rating']
                actualones.append(info[i])

        return render_template("buypage.html", info=actualones)
    else:
        search = request.form['searchQuery']
        return redirect(url_for('search', query=search))


@app.route("/itempage/<email>/<bookName>/<author>/<price>/<condition>", methods=['GET','POST'])
@requireLogin
def itempage(email, bookName, author, price, condition):
    if request.method == "GET":
        info = database.listAll()
        for i in range(len(info)):
            if email == info[i]['email'] and bookName == info[i]['bookName'] and author == info[i]['author'] and price == info[i]['price'] and condition == info[i]['condition']:
                thisBook = info[i]
                userRating = database.getUserRating(email)
                currUser = session['email']
                return render_template("itempage.html", thisBook=thisBook, userRating=userRating, currUser=currUser)
    else:
        search = request.form['searchQuery']
        return redirect(url_for('search', query=search))

@app.route('/edit/<bookName>', methods=['GET', 'POST'])
@requireLogin
def edit(bookName):
    if request.method == 'GET':
        bookName = bookName.replace("%20", " ")
        email = session['email']
        bookInfo = database.getBookInfo(bookName, email)
        if bookInfo == None:
            return redirect(url_for('userpage'), msg = 'You can only edit a book that you own.')
        return render_template("edit.html", bookInfo=bookInfo)
    else:
        if request.form['signup'] == "edit":
            email = session['email']
            title = request.form['title']
            author = request.form['author']
            isbn = request.form['serial']
            subject = request.form['subject']
            condition = request.form['condition']
            price = request.form['price']
            image_url = get_image_url( title + author + isbn )

            database.updateBookInfo(bookName ,email, title, author, isbn, subject, condition, price, image_url)
            return redirect(url_for('userpage'))
        elif request.form['signup'] == "search":
            search = request.form['searchQuery']
            return redirect(url_for('search', query=search))

@app.route('/search', methods=["GET","POST"])
@requireLogin
def search():
    if request.method=="POST":
        search = request.form['searchQuery']
        return redirect(url_for('search', query=search))
    else:
        search = request.args.get("query")
        results = ranking.searchForBook(search)
        return render_template("search.html", info=results)

@app.route('/finish/<email>/<bookName>/<author>/<price>/<condition>')
@requireLogin
def finish(email, bookName, author, price, condition):
    bookName = bookName.replace("%20", " ")

    sellerEmail = email + '@stuy.edu'
    buyerEmail = database.getBuyerEmail(email, bookName, author, price, condition) + '@stuy.edu'
    rateLink = 'stuybooks.stuycs.org/userpage#bought'

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
    #TODO send link to rate
    textB = '''
    Hello,

    Our records indicate that you have bought %s for $%s. The seller has confirmed that you have received the book.
    Please rate the transaction at: %s
    If you have not received your book contact us immediately at %s

    Yours,
    Team JASH''' %(bookName, price, rateLink, ourEmail)

    messageB.attach(MIMEText(textB, 'plain'))
    s.sendmail(ourEmail, buyerEmail, messageB.as_string())

    s.close()

    database.setBookStatus(bookName, email, author, price, condition, 'sold')

    return redirect(url_for('userpage'))

@app.route('/bought/<email>/<bookName>/<author>/<price>/<condition>', methods=['GET', 'POST'])
@requireLogin
def bought(email, bookName, author, price, condition):

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
    Hello,

    You have listed the book %s for sale for $%s. We are pleased to say that
    someone has seen the offer and will gladly meet up with you to purchase the book.

    Feel free to reach out to the buyer at %s to set up a convenient meeting location.

    If you are unsure as to an appropriate meeting spot, here are a few recommendations:
    The Senior Bar/Atrium (2nd Floor)
    Bridge Entrance (2nd Floor)
    The Half-Floor
    The Guidance Office ( Rm. 236 )
    The First Floor Atrium

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
    Hello,

    You have indicated that you want to buy the book %s for $%s.

    Feel free to reach out to the seller at %s to set up a convenient meeting location.

    If you are unsure as to an appropriate meeting spot, here are a few recommendations:

    The Senior Bar/Atrium (2nd Floor)
    Bridge Entrance (2nd Floor)
    The Half-Floor
    The Guidance Office ( Rm. 236 )
    The First Floor Atrium

    Yours,
    Team JASH''' %(bookName, price, sellerEmail)

    messageB.attach(MIMEText(textB, 'plain'))
    s.sendmail(ourEmail, buyerEmail, messageB.as_string())

    s.close()

    database.setBookStatus(bookName, email, author, price, condition, 'pending')
    database.setBuyerEmail(bookName, email, author, price, condition, session['email'])

    return redirect(url_for('userpage'))

@app.route('/cancel/<email>/<bookName>/<author>/<price>/<condition>')
@requireLogin
def cancel(email, bookName, author, price, condition):
    bookName = bookName.replace('%20', ' ')
    author = author.replace('%20', ' ')
    database.setBookStatus(bookName, session['email'], author, price, condition, 'available')
    database.setBuyerEmail(bookName, session['email'], author, price, condition, '')

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
    Hello,

    You indicated that you wanted %s for $%s. The seller has canceled this transaction.
    If this is a mistake you can contact the seller at %s.

    Yours,
    Team JASH''' %(bookName, price, email + '@stuy.edu')

    message.attach(MIMEText(text, 'plain'))
    s.sendmail(ourEmail, session['email'] + '@stuy.edu', message.as_string())

    s.close()

    database.setBookStatus(bookName, email, author, price, condition, 'available')
    database.setBuyerEmail(bookName, email, author, price, condition, session['email'])
    return redirect(url_for('userpage'))

@app.route('/remove/<email>/<bookName>/<author>/<price>/<condition>')
@requireLogin
def remove(email, bookName, author, price, condition):
    bookName = bookName.replace("%20", " ")
    author = author.replace('%20', ' ')
    database.deleteAllBooks(email, bookName, author, price, condition)
    return redirect(url_for('userpage'))

@app.route('/rate1', methods=['GET', 'POST'])
def rate1():
    if request.method == 'GET':
        return render_template("rate.html")
    else:
        if request.form["signup"] == "Submit":
            rating = request.form['rating']
            print rating
            return redirect(url_for('home'))
        elif request.form["signup"] == "search":
            search = request.form['searchQuery']
            return redirect(url_for('search', query=search))

@app.route('/rate')
@app.route('/rate/<buyerEmail>/<sellerEmail>/<bookName>/<author>/<price>/<condition>/<up>', methods=['GET', 'POST'])
@requireLogin
def rate(buyerEmail, sellerEmail, bookName, author, price, condition, up):
    if request.method == 'POST':
        buyerEmail = session['email']
        if request.args.get("rate")!= None:
            rating = request.args.get("rate")
            print rating

            if up == True or rating == str(2): # upvote
                print "upvoting"
                database.upvoteBook(sellerEmail, bookName, author, price, condition)
            elif up == False or rating == str(1): # downvote
                print "downvoting"
                database.downvoteBook(sellerEmail, bookName, author, price, condition)

            return redirect(url_for("itempage"))
        else:
            rated = database.getBookRating(sellerEmail, bookName, author, price, condition)
            if rated == None or rated == 0:
                print "to be rated"
                return redirect(url_for("itempage"))
#                return render_template('rate.html', message="to be rated", buyerEmail=buyerEmail, sellerEmail=sellerEmail, bookName=bookName, author=author, price=price, condition=condition, email=buyerEmail)
            else:
                print "already rated"
                return redirect(url_for("userpage"))
    else:
        if request.form["signup"] == "search":
            search = request.form['searchQuery']
            return redirect(url_for('search', query=search))

@app.route('/report/<reporterEmail>/<email>/<bookName>/<author>/<price>/<condition>')
@requireLogin
def report():
    bookName = bookName.replace('%20', ' ')
    author = author.replace('%20', ' ')

    #Report the seller for inappropriate behavior
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(ourEmail, ourPassword)

    report = MIMEMultipart()
    report['Subject'] = 'Inappropriate Conduct by User'
    report['From'] = ourEmail
    report['To'] = siteAdmin

    adminMessage = '''
    Dear Administrator,

    %s has reported %s for inappropriate behavior.
    Please reach out to the users and take appropriate action.

    Yours,
    Team JASH
    ''' %(reporterEmail + '@stuy.edu', email + '@stuy.edu')

    report.attach(MIMEText(adminMessage, 'plain'))
    s.sendmail(ourEmail, siteAdmin, report.as_string())

    message = MIMEMultipart()
    message['Subject'] = 'Inappropriate Conduct'
    message['From'] = ourEmail
    message['To'] = email + '@stuy.edu'

    text = '''
    Hello,

    Someone has reported you for misconduct. An email has been sent out to the website administrator, who will reach out to you at as soon as possible.

    If you believe this to be a mistake, please feel free to resolve it with the administrator.

    Yours,
    Team JASH
    '''

    message.attach(MIMEText(text, 'plain'))
    s.sendmail(ourEmail, email + '@stuy.edu', message.as_string())

    message = MIMEMultipart()
    message['Subject'] = 'Your Report Has Been Submitted'
    message['From'] = ourEmail
    message['To'] = reporterEmail + '@stuy.edu'

    text = '''
    Hello,

    Your report has been successfully filed for the following book: %s.

    A site administrator may contact you for additional information.

    Thank you for your support in keeping StuyBooks safe.

    Yours,
    Team JASH

    If you believe this message to be in error, please reply to this email.
    ''' %(bookName)

    message.attach(MIMEText(text, 'plain'))
    s.sendmail(ourEmail, reporterEmail + '@stuy.edu', message.as_string())

    s.close()

    database.setBookStatus(bookName, email, author, price, condition, 'inappropriate')
    return redirect(url_for('userpage'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('home'))

#------------------ Administrator Functions ------------------#
@app.route('/admin', methods=['GET', 'POST'])
@requireLogin
@requireAdmin
def admin():
    if request.method == 'GET':
        unapproved = image.getUnapprovedImageUrls()
        print unapproved
        return render_template('userpage.html', admin=True, unapproved=unapproved)
    else:
        unapproved = image.getUnapprovedImageUrls()
        print unapproved
        return render_template('userpage.html', admin=True, unapproved=unapproved)

@app.route('/approve/<image_url>')
@requireLogin
@requireAdmin
def approve():
    image.changeImageStatus(image_url, 'unapproved', 'approved')
    return redirect(url_for('admin'))

@app.route('/veto/<image_url>')
@requireLogin
@requireAdmin
def veto():
    image.changeImageStatus(image_url, 'unapproved', 'vetoed')
    return redirect(url_for('admin'))

if __name__ == "__main__":
    app.debug = True # change to false when deploying
    app.secret_key = str(uuid4())
    app.run()
