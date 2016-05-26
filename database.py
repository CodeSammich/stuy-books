# Authors: Samuel Zhang, Jeffrey Zou
# Description: Deals with the database

from pymongo import MongoClient
import gridfs

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
def addUser(email, passwordHash, status=0):
    '''
    Adds user to the database
    Args:
        email (string)
        passwordHash (string)
        status (integer) 0 for inactive, 1 for active
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
        'email': replaceApostrophe(email.strip('@stuy.edu')),
        'passwordHash': passwordHash,
        'status': 0
        #'first': first,
        #'last': last
    })

#    user_account = accounts.find_one( {'email': email})
#    print user_account['email']
    return ''

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
    result = db.accounts.find_one({'email': email})
    if len(result) == 0:
        return False
    else:'''
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

#------------------------- Book keeping -------------------------#
def addBook(email, bookName, author, isbn, subject, condition, price, description):
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
        description (string)
    Empty string if information doesn't exist
    Email + bookName will never be empty
    Returns:
        True
    '''
    db = client['books-database']
    books = db['books']
    image_url = get_image_url( bookName + author + isbn )
    books.insert_one({'email':email,
                      'bookName': bookName,
                      'author': author,
                      'isbn': isbn,
                      'subject': subject,
                      'condition': condition,
                      'price': price,
                      'description': description,
                      'image_url': image_url})
    return True

def deleteBook(email, bookName):
    '''
    Deletes the first appearance of a book under a seller
    Args:
        email (string)
        bookName (string)
    Returns:
        True
    '''
    db = client['books-database']
    books = db['books']
    books.find_one_and_delete({'email': email, 'bookName': bookName})
    return True

# image scraping for Google
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
<<<<<<< HEAD
    
def delete_book( bookName, email ):
    db = client['books-database']
    books = db['books']
    results = books.remove( {'email': email,
                             'bookName': bookName },
                            True ) # delete justOne = True
    
=======
>>>>>>> dfd41e83133cd0fba1936434069ad250deb9e8a4

delete_account( "szhang5" )
