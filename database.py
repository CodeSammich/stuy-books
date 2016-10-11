'''
Authors: Samuel Zhang, Jeffrey Zou
Description: Deals with accounts, books, and related operations

Requires MongoDB Installation, please refer to README.md

------------------------------------
DATABASE DESIGN NOTES:

MONGO:

Database Structure:
Database
---- Collections

Ex.
"accounts-database"
---- "accounts"
--------- 'email'
--------- 'passwordHash'
--------- etc.


CURRENT DATABASES:

'accounts-database': Users' accounts, including sysadmin
--- 'email'
--- 'passwordHash'
--- 'status' : 0: unactivated, 1: activated
--- 'reset' : used only for resetting passwords
--- 'userRating' : user's public rating *
--- 'upvotes' : number of upvotes user received **
--- 'downvotes' : number of downvotes user received **
--- 'votes' : total number of votes user received

     *  not used for ranking
     ** 'upvotes', 'downvotes' are total of each book's 'rating' (See below)

'books-database': Book database
--- 'email' : seller's email
--- 'bookName'
--- 'author'
--- 'isbn'
--- 'subject'
--- 'condition' : condition of book (e.g. New, Acceptable, Used)
--- 'price'
--- 'image_url' : image used for thumbnail, see 'image.py' for details
--- 'status': book's availability; 'Available', 'Pending', 'Sold'
--- 'buyerEmail': potential buyer's email
--- 'rating' : book's rating (+1, 0, -1) ***
--- 'search_priority' : used only for search ranking algorithm, no direct access ***

    *** Please see 'ranking.py' for details

'''


from pymongo import MongoClient

#from search import *
#from image import *
import image

#------------------------- Establish MongoDB Connection ----------------#
client = MongoClient()

#------------------------- Account Management ---------------------------#
def addUser(email, passwordHash, status=0, reset=''):
    '''
    Adds user to the database
    Args:
        email (string)
        passwordHash (string)
        status (integer) 0 for inactive, 1 for active
        reset (string) reset code if person forgets password
    Returns:
        String with errors, or empty string if there aren't any
    '''
    dbnames = client.database_names()
#    print dbnames
    db = client['accounts-database']

    accounts = db['accounts']

    if 'accounts-database' not in dbnames: #init database and collection
        dummy_pass = "dummy_pass" #may need to be more secure
        init_account = {
            'email': 'dummy_email@stuy.edu',
            'passwordHash': dummy_pass,
            'status': 0
        }
        init_id = accounts.insert_one( init_account).inserted_id #dummy account

    user_account = accounts.find_one({'email': email})

    if user_account != None:
        return 'An account has already been registered under this email'
    accounts.insert_one({
        'email': email,
        'passwordHash': passwordHash,
        'status': status,
        'reset': '',
        'userRating': 0, #from 0 to 5
        'upvotes': 0,
        'downvotes': 0,
        'votes': 0
        #'first': first,
        #'last': last
    })
    return ''

def authenticate(email, passwordHash):
    '''
    Checks to see if email and password exist in the database
    args:
        email (string)
        passwordHash (string)
    Returns:
        True if the password and email exist in the database, False otherwise
    '''
    db = client['accounts-database']
    accounts = db['accounts']
    #definitely only 1 acc.
    result = accounts.find_one({'email': email, 'passwordHash': passwordHash, 'status': 1})
    if result == None:
        return False
    #if not getStatus(email):
        #return False
    return True

def hasReset(code):
    '''
    Looks for the user with a reset code and sets it back to empty string
    Args:
        code (string)
    Returns:
        True
    '''
    db = client['accounts-database']
    accounts = client['accounts']
    accounts.find_one_and_update(
        {'reset': code},
        {
            '$set': {'reset': ''}
        }
    )
    return True

#---------------------- Get Functions ------------------------#
def getUser(email):
    '''
    Gets the document for a user from the db
    Args:
        email (string)
    Returns:
        Dictionary of data, or None
    '''
    db = client['accounts-database']
    accounts = db['accounts']
    return accounts.find_one({'email': email})


def getStatus(email):
    '''
    Gives the status of an account
    Args:
        email (string)
    Returns:
        True if active, False otherwise
    '''
    db = client['accounts-database']
    accounts = db['accounts']
    results = accounts.find_one({'email': email})
    if results == None:
        return False
    if results['status'] == 0:
        return False
    return True

def getEmailFromReset(code):
    '''
    Gets a user's email from reset code (only use when resetting, pretty much impossible elsewhere)
    Args:
        code (string)
    Returns:
        The email (string) or None
    '''
    db = client['accounts-database']
    accounts = db['accounts']
    result = accounts.find_one({'reset': code})
    return result['email'] or None

def getUserRating(email):
    '''
    Gets a user's net rating
    Args:
        email (string)
    Returns:
        rating (integer)
    '''
    db = client['accounts-database']
    accounts = db['accounts']
    user = accounts.find_one({'email': email})
#    print user
    #return user['userRating'] or None
    try:
        print "database user rating upvotes: "
        print user['upvotes']
        return user['upvotes'] - user['downvotes']
    except KeyError:
        return 0

def getUpvotes():
    '''
    Gets a user's upvotes
    Args:
        email (string)
    Returns:
        upvotes (integer)
    '''
    db = client['accounts-database']
    accounts = db['accounts']
    user = accounts.find_one({'email': email})
    try:
        return user['upvotes']
    except KeyError:
        return 0

def getDownvotes():
    '''
    Gets a user's downvotes
    Args:
        email (string)
    Returns:
        downvotes (integer)
    '''
    db = client['accounts-database']
    accounts = db['accounts']
    user = accounts.find_one({'email': email})
    try:
        return user['downvotes']
    except KeyError:
        return 0

def getNumberVotes(email):
    '''
    Get the number of voters for user
    Args:
        email (string)
    Returns:
        votes (integer)
    '''
    db = client['accounts-database']
    accounts = db['accounts']
    try:
        return accounts.find_one({'email': email})['votes']
    except KeyError:
        return 0

def getBookStatus(bookName):
    '''
    Gets the status of a book
    Args:
        bookName (string)
    Returns:
        Status of the book
    '''
    db = client['books-database']
    books = db['books']
    results = books.find_one({'bookName': bookName})
    return results['status']

def getBookInfo(bookName, email):
    '''
    Gets the info of a book
    Args:
        bookName (string)
        email (string)
    Returns
        List containing book info
        [ bookName (string)
        author (string)
        isbn (string)
        subject (string)
        condition (string)
        price (string)
        buyerEmail (string) ]
    '''
    db = client['books-database']
    books = db['books']
    results = books.find_one({'bookName': bookName, 'email': email})
    if results == None:
        return None
    return {'bookName': results['bookName'],
            'author': results['author'],
            'isbn': results['isbn'],
            'subject': results['subject'],
            'condition': results['condition'],
            'price': results['price'],
            'buyerEmail': results['buyerEmail'],
            }

def getSellersForBook(bookName):
    '''
    Looks up people who are selling a book
    Args:
        bookName (string)
    Returns:
        A list of sellers for the book
    '''
    db = client['books-database']
    books = db['books']
    results = books.find({'bookName', bookName})
    #return [results[i]['email'] for i in range(results.count)]
    people = []
    for r in results:
        people.append[r]
    #remove duplicates
    seen = set()
    seenmore = seen.add
    return [x for x in people if not (x in seen or x in seenmore(x))]

def getBuyerEmail(email, bookName, author, price, condition):
    '''
    Gets the buyer email for a book
    Args:
        email (string)
        bookName (string)
        author (sting)
        price (string)
        condition (string)
    Returns:
        buyerEmail (string)
    '''
    db = client['books-database']
    books = db['books']
    return books.find_one({'email': email, 'bookName': bookName, 'author': author, 'price': price, 'condition': condition})['buyerEmail']

def getBookRating(email, bookName, author, price, condition):
    '''
    Gets the rating for a book
    Args:
        email (string)
        bookName (string)
        author (sting)
        price (string)
        condition (string)
    Returns:
        rating (None/integer)
    '''
    db = client['books-database']
    books = db['books']
    return books.find_one({'email': email, 'bookName': bookName, 'author': author, 'price': price, 'condition': condition})['rating']

#---------------------- Set Functions ------------------------#

def updateStatus(email):
    '''
    Updates the status of an account
    Args:
        email (string)
    Returns:
        True
    '''
    db = client['accounts-database']
    accounts = db['accounts']
    accounts.find_one_and_update(
        {'email': email},
        {'$set': {'status': 1}}
    )
    return True

def updatePassword(email, newPasswordHash):
    '''
    Updates the password for the user
    Args:
        email (string)
        newPasswordHash (string)
    Returns:
        True if successful, False otherwise
    '''
    db = client['accounts-database']
    try:
        db.accounts.update_one(
            {'email':email},
            {
                '$set': {'passwordHash': newPasswordHash}
            }
        )
    except: # catch *all* exceptions
        return False
    return True

def setReset(email, code):
    '''
    Sets the reset code for a user
    Args:
        email (string)
        code (string)
    Returns:
        True
    '''
    db = client['accounts-database']
    accounts = db['accounts']
    accounts.update_one(
        {'email': email},
        {
            '$set': {'reset': code}
        }
    )
    return True

def changeUserRating(email, rating):
    '''
    Changes the user rating by averaging it with the new rating
    Args:
        email (string)
        new rating (integer)
    Returns:
        True
    '''
    db = client['accounts-database']
    accounts = client['accounts']
    user = accounts.find_one({'email': email})
    oldRating = user['rating']
    raters = user['raters']
    accounts.find_one_and_update(
        {'email': email},
        {'$set': {'rating': (oldRating * raters + rating)/(raters + 1), 'raters': raters + 1}}
    )
    return True

#------------------------- Book keeping -------------------------#
## Assume price/condition doesn't change unless edited, different conditions/prices
## should be separate entries. (make note in frontend)
def addBook(email, bookName, author, isbn, subject, condition, price, status='available'):
    '''
    Updates the books that are being sold and the user that is selling
    Args:
        email (string)
        bookName (string)
        author (string)
        isbn (string)
        subject (string)
        condition (string)
        price (string)
        status (string) available, pending, sold, inappropriate

    Empty string if information doesn't exist

    Email + bookName will never be empty

    Returns:
        True if this book does not exist under the user, False if it does
    '''
    db = client['books-database']
    books = db['books']

    image_url = image.get_image_url( bookName + author + isbn )
    results = books.find_one({'email': email, 'bookName':bookName, 'author': author, 'price': price, 'condition': condition})
    if results == None:
        books.insert_one({'email':email,
                          'bookName': bookName,
                          'author': author,
                          'isbn': isbn,
                          'subject': subject,
                          'condition': condition,
                          'price': price,
                          'image_url': image_url,
                          'status': status,
                          'buyerEmail': '',
                          'rating': None,
                          'search_priority': None #ONLY FOR SEARCH: SEE 'ranking.py'
                          })
        return True
    return False

def deleteAllBooks(email, bookName, author, price, condition):
    '''
    Deletes all copies of a book under a seller
    Args:
        email (string)
        bookName (string)
        author (string)
        price (string)
        condition (string)
    Returns:
        True
    '''
    db = client['books-database']
    books = db['books']
    books.find_one_and_delete({'email': email, 'bookName': bookName, 'author': author ,'price': price, 'condition': condition})
    return True


#------------------------- Set Functions -------------------------#
def updateBookInfo(oldName, email, bookName, author, isbn, subject, condition, price, image_url):
    '''
    Updates the book in the database for a book owned by a user (note neither the owner nor the title are changed)
    Args:
        oldName (string)
        email (string)
        bookName (string)
        author (string)
        isbn (string)
        subject (string)
        condition (string)
        price (string)
        image_url (string)
    Returns:
        True
    '''
    db = client['books-database']
    books = db['books']
    if bookName.strip() != '':
        books.find_one_and_update(
            {'email': email, 'bookName': oldName},
            {'$set': {'bookName': bookName}}
        )
    if author.strip() != '': #Returns True if author is not empty
        books.find_one_and_update(
            {'email': email, 'bookName': oldName},
            {'$set': {'author': author}}
        )
    if isbn.strip() != '':
        books.find_one_and_update(
            {'email': email, 'bookName': oldName},
            {'$set': {'isbn': isbn}}
        )
    if subject.strip() != '':
        books.find_one_and_update(
            {'email': email, 'bookName': oldName},
            {'$set': {'subject': subject}}
        )
    if condition.strip() != '':
        books.find_one_and_update(
            {'email': email, 'bookName': oldName},
            {'$set': {'condition': condition}}
        )
    if price.strip() != '':
        books.find_one_and_update(
            {'email': email, 'bookName': oldName},
            {'$set': {'price': price}}
        )
    if image_url.strip() != '':
        books.find_one_and_update(
            {'email': email, 'bookName': oldName},
            {'$set': {'image_url': image_url }}
        )
    return True


def setBuyerEmail(bookName, sellerEmail, author, price, condition, buyerEmail):
    '''
    Sets the email for the buyer for a book
    Args:
        bookName (string)
        sellerEmail (string)
        author (string)
        price (string)
        condition (string)
        buyerEmail (string)
    Returns:
        True
    '''
    db = client['books-database']
    books = db['books']
    books.find_one_and_update(
        {'bookName': bookName, 'email': sellerEmail, 'author': author, 'price': price, 'condition': condition},
        {'$set': {'buyerEmail': buyerEmail}}
    )
    return True

def setBookStatus(bookName, email, author, price, condition, stat):
    '''
    Sets the status of a book
    Args:
        bookName (string)
        email (string)
        author (string)
        price (string)
        condition (string)
        stat (string)
    Returns:
        True
    '''
    db = client['books-database']
    books = db['books']
    books.find_one_and_update(
        {'bookName': bookName, 'email': email, 'author': author, 'price': price, 'condition': condition},
        {'$set': {'status': stat}}
    )
    return True

def upvoteUser( email ):
    '''
    Upvotes a particular user
    '''
    db = client['accounts-database']
    accounts = db['accounts']
    user = accounts.find_one( {'email': email} )

    if user['upvotes'] == None:
        print "user upvote to 1"
        user['upvotes'] = 1
    else:
        print "user vote incremented"
        user['upvotes'] += 1
        print user['upvotes']

    if user['votes'] == None:
        print "user vote to 1"
        user['votes'] = 1
    else:
        user['votes'] += 1 # total number of votes

    accounts.find_one_and_update(
        {'email': email},
        {'$set': {'upvotes': user['upvotes']}}
    )

    accounts.find_one_and_update(
        {'email': email},
        {'$set': {'vote': user['votes']}}
    )

def upvoteBook(email, bookName, author, price, condition):
    '''
    Upvotes a book's rating and seller
    For more info on book rating vs. user rating, check 'ranking.py'
    Args:
        email (string)
        bookName (string)
        author (sting)
        price (string)
        condition (string)
    Returns:
        True
    '''
    db = client['books-database']
    books = db['books']
    book = books.find_one({'email': email, 'bookName': bookName, 'author': author, 'price': price, 'condition': condition})

    current_rating = book['rating']
    if current_rating == None:
        book['rating'] = 1
        current_rating = 1
    else:
        book['rating'] = current_rating + 1
        current_rating += 1

    books.find_one_and_update(
        {'email': email, 'bookName': bookName},
        {'$set': {'rating': current_rating}}
    )

    # Upvote user as well
    upvoteUser( email )
    return True

def downvoteUser( email ):
    '''
    Downvotes a particular user
    '''
    db = client['accounts-database']
    accounts = db['accounts']
    user = accounts.find_one( {'email': email} )

    if user['downvotes'] == None:
        user['downvotes'] = 1
    else:
        user['downvotes'] += 1
        print user['downvotes']

    if user['votes'] == None:
        print "user vote to 1"
        user['votes'] = -1
    else:
        user['votes'] -= 1 # total number of votes

    accounts.find_one_and_update(
        {'email': email},
        {'$set': {'downvotes': user['downvotes']}}
    )

    accounts.find_one_and_update(
        {'email': email},
        {'$set': {'vote': user['votes']}}
    )


def downvoteBook(email, bookName, author, price, condition):
    '''
    Downvotes a book's rating and seller
    For more info on book rating vs. user rating, check 'ranking.py'
    Args:
        email (string)
        bookName (string)
        author (sting)
        price (string)
        condition (string)
    Returns:
        True
    '''
    db = client['books-database']
    books = db['books']
    book = books.find_one({'email': email, 'bookName': bookName, 'author': author, 'price': price, 'condition': condition})

    current_rating = book['rating']
    if current_rating == None:
        book['rating'] = -1
    else:
        book['rating'] -= 1

    books.find_one_and_update(
        {'email': email, 'bookName': bookName},
        {'$set': {'rating': book['rating']}}
    )
    
    # Downvote seller as well
    downvoteUser( email )
    return True

#-------------------------- Book list functions --------------------#

def listBooksForUser(email):
    '''
    Looks for books under a single user
    Args:
        email (string)
    Returns:
        A list of documents under an email
    '''
    db = client['books-database']
    books = db['books']
    results = books.find({'email': email})
    docs = []
    for r in results:
        docs.append(r)
    return docs

def listBoughtForUser(email):
    '''
    Looks for books that have been bought by a user
    Args:
        email (string)
    Returns:
        A list of documents for which buyerEmail is the email
    '''
    db = client['books-database']
    books = db['books']
    results = books.find({'buyerEmail': email, 'status': 'sold'})
    docs = []
    for r in results:
        docs.append(r)
    return docs

def listAll():
    '''
    Returns the entire collection of books
    Args:
        None
    Returns:
        The entire database in a list
    '''
    db = client['books-database']
    books = db['books']
    results = books.find({})
    all = []
    for r in results:
        all.append(r)
    return all

# -------------------- Clean Database ---------------------- #
def deleteAccount( email ): #without @stuy.edu
    db = client['accounts-database']
    accounts = db['accounts']
    accounts.find_one_and_delete( {'email': email })

def deleteBook( bookName, email ):
    db = client['books-database']
    books = db['books']
    results = books.remove( {'email': email,
                             'bookName': bookName },
                            True ) # delete justOne = True

#------------------------- Admin Functions ----------------#

''' Work in Progress '''
