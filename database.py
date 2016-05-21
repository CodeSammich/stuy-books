# Authors: Jeffrey Zou
# Description: Deals with the database

from pymongo import MongoClient

connection = MongoClient()

def replaceApostrophe(s):
    return s.replace("'", '&#8217')

#------------------------- Setup User -------------------------#
def addUser(email, passwordHash, first, last):
    '''
    Adds user to the database
    Args:
        email (string)
        passwordHash (string)
        first (string): first name of the user
        last (string): last name of the user
    Returns:
        String with errors, or empty string if there aren't any
    '''
    db = connection['Users']
    useraccounts = db.accounts.find({'email':email})
    if len(useraccounts) != 0:
        return 'An account has already been registered under this email'
    db.accounts.insert_one({
        'email': replaceApostrophe(email),
        'passwordHash': passwordHash,
        'first': first,
        'last': last
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
    db = connection['Users']
    '''result = db.accounts.find_one({'email': email}) #definitely only 1 acc.
    if len(result) == 0:
        return False '''
    try
        db.accounts.find( {'email':email, 'password':passwordHash } )
    except:
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
    '''
'''    result = db.accounts.find_one({'email': email})
    if len(result) == 0:
        return False
    else:'''
    db = connection['Users']
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
