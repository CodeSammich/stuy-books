# Authors: Samuel Zhang, Jeffrey Zou
# Description: Deals with the database (if that wasn't obvious)

from pymongo import MongoClient
#import gridfs

# Google Image
from bs4 import BeautifulSoup
import urllib2
import re
#------------------------- Establish MongoDB Connection ----------------#
client = MongoClient()

#### Data is stored in databases, under which are collections.
#### Ex. "accounts-database" is a database, and "accounts" is the collection
#### "accounts" contains all the "Documents" that have each user's information

def replaceApostrophe(s):
    return s.replace("'", '&#8217')

#------------------------- Setup User -------------------------#
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
    db = client['accounts-database']

    accounts = db['accounts']

    if 'accounts-database' not in dbnames: #init database and collection
        print 'database initialized'
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
        'email': replaceApostrophe(email.replace('@stuy.edu', '')),
        'passwordHash': passwordHash,
        'status': 0,
        'reset': ''
        #'first': first,
        #'last': last
    })

#    user_account = accounts.find_one( {'email': email})
#    print user_account['email']
    return ''

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
    print "not none"
    print results
    if results['status'] == 0:
        return False
    return True

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
    for r in accounts.find({}):
        print r['email']
    return True

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
    result = accounts.find_one({'email': email, 'passwordHash': passwordHash})
    if result == None:
        return False
    #if not getStatus(email):
        #return False
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
        status (string) available, pending, sold

    Empty string if information doesn't exist

    Email + bookName will never be empty

    Returns:
        True if this book does not exist under the user, False if it does
    '''
    db = client['books-database']
    books = db['books']

    image_url = get_image_url( bookName + author + isbn )
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
                          'buyerEmail': ''
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

"""
def deleteSingleBook(email, bookName):
    '''
    Deletes only one copy of a book for a seller
    DO NOT CALL UNLESS YOU ARE SURE THERE IS AT LEAST ONE BOOK
    Args:
        email (string)
        bookName (string)
    Returns:
        True
    '''
    db = client['books-database']
    books = db['books']
    results = books.find_one({'email': email, 'bookName': bookName})
    if results['quantity'] == 1:
        books.delete_one({'email': email, 'bookName': bookName})
    else:
        books.find_one_and_update(
            {'email': email, 'bookName': bookName},
            {'$inc': {'quantity': -1}}
        )
    return True
"""

def updateBookInfo(oldName, email, bookName, author, isbn, subject, condition, price):
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
    return True

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
"""
def addBuyerEmail(bookName, sellerEmail, buyerEmail):
    '''
    Add a buyer to the books
    Args:
        bookName (strings)
        sellerEmail (string)
        buyerEmail (string)
    Returns:
        True
    '''
    db = client['books-database']
    books = db['books']
    results = find_one({'email': sellerEmail, 'bookName': bookName})
    books.find_one_and_update(
        {'email': sellerEmail,'bookName': bookName},
        {'$set': {'buyerEmails': results['buyerEmails'].append(buyerEmail)}}
    )
    return True

def getCount(bookName, email):
    '''
    Gets the # of books available for a user
    Args:
        bookName (String)
        email (String)
    Returns
        # of books
    '''
    db = client['books-database']
    books = db['books']
    results = books.find_one({'email':email, 'bookName':bookName})
    return results['quantity'] or 0
"""

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

# ------------------------ Image Scraping from Google --------------#
def get_soup(url, header):
    '''
    Helper function for get_image_url
    Input:
        url (string)
        header (string)
    Output:
        Blaaah
    '''
    return BeautifulSoup( urllib2.urlopen(urllib2.Request(url,headers=header)), "html.parser" )

def get_image_url(query):
    '''
    Returns the url of the first google image with found using query
    Input:
        query (string)
    Output:
        url (string)
    '''
    query = query.split()
    query = '+'.join(query)
    url = "https://www.google.co.in/search?q="+query+"&source=lnms&tbm=isch"
    print url + "\n\n"
    header = {'User-Agent': 'Mozilla/5.0'}
    soup = get_soup(url,header)


    images = [a['src'] for a in soup.find_all("img", {"src": re.compile("gstatic.com")})]

    for i in images:
        i = str(") + i + str(")

    #for second choice, return images[1], etc.
    return images[0]



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
def delete_account( email ): #without @stuy.edu
    db = client['accounts-database']
    accounts = db['accounts']
    accounts.find_one_and_delete( {'email': email })

def delete_book( bookName, email ):
    db = client['books-database']
    books = db['books']
    results = books.remove( {'email': email,
                             'bookName': bookName },
                            True ) # delete justOne = True

# -------------------------Search Function -----------------#

def searchForBook(query):
    '''
    Looks up a list book given a simple search query (no logical operators)
    Args:
        query (string)
    Returns:
        A list of books with that name/author
    '''
    db = client['books-database']
    books = db['books'] #collection

    #parse query to find relevant results
    results = []
    query = query.strip(',')
    query = query.split(' ')
    print query
    for j in range(len(query)): #goes through query

        # goes through database to find books with query[j] in substring value
        cursor = books.find( {'bookName':
                              { '$regex' : '.*' + query[j] + '.*' } } )
        for b in cursor:
            print b['bookName']
            print 'book found, going to next book'
            if not b in results:
                results.append( b )
                #break; #goes to next book

        cursor = books.find( {'author':
                      { '$regex' : '.*' + query[j] + '.*' } } )
        for b in cursor:
            print b['bookName']
            print 'book found, going to next book'
            if not b in results:
                results.append( b )
                #break; #goes to next book

        cursor = books.find( {'isbn':
                              { '$regex' : '.*' + query[j] + '.*' } } )
        for b in cursor:
            print b['bookName']
            print 'book found, going to next book'
            if not b in results:
                results.append( b )
                #break; #goes to next book

    return results
