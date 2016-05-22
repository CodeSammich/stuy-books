# Authors: Samuel Zhang, Jeffrey Zou
# Description: Deals with the database

from pymongo import MongoClient

#------------------------- Establish MongoDB Connection ----------------#
client = MongoClient()

#### Data is stored in databases, under which are collections.
#### Ex. "accounts-database" is a database, and "accounts" is the collection
#### "accounts" contains all the "Documents" that have each user's information

def replaceApostrophe(s):
    return s.replace("'", '&#8217')

#------------------------- Setup User -------------------------#
def addUser(email, passwordHash):
    '''
    Adds user to the database
    Args:
        email (string)
        passwordHash (string)
    Returns:
        String with errors, or empty string if there aren't any
    '''
    print 'starting'
    dbnames = client.database_names()
    print 'next'
    db = client['accounts-database']
    print 'database called'
    accounts = db['accounts']
    print 'before empty db test'
    if 'accounts-database' not in dbnames: #init database and collection
        print 'database initialized'
        #generating password hex for init account
        m = sha256()
        m.update( "dummy_password" ) #may need to be more secure
        dummy_pass = m.hexdigest()
        init_account = {
            'email': 'dummy_email@stuy.edu',
            'passwordHash': dummy_pass,
        }
        init_id = accounts.insert_one( init_account).inserted_id #dummy account
    print 'after empty test'
    user_account = accounts.find_one({'email': email})
    print "looked through db"
    if user_account != None:
        print 'no go'
        return 'An account has already been registered under this email'
    accounts.insert_one({
        'email': replaceApostrophe(email),
        'passwordHash': passwordHash
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
    result = accounts.find_one({'email': email}) #definitely only 1 acc.
    if result == None:
        return False
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
