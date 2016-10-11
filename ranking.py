'''
Authors: Helen Li, Samuel Zhang
Description: Ranking algorithm for search engine


------------------------------------------------
RANKING DESIGN NOTES:

Search Engine ranking algorithm based on Reddit's comment algorithm and uses the Wilson Score Interval

More info on the mathematics and implementation:
- https://medium.com/hacking-and-gonzo/how-reddit-ranking-algorithms-work-ef111e33d0d9#.4mypka6yx
- https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval#Wilson_score_interval


USER:
A user can be upvoted/downvoted and has a rating based on confidence.

BOOK:
A book can only have a single rating:
   - +1, 0, -1
   - If multiple copies, it'll be still positive, 0, or negative
   - Sign is used to indicate result by book, rather than a specific number


Not to be confused with 'rating', a book also has a 'search_priority' element*

    * NOTE: To avoid conflicts, 'search_priority' IS ONLY USED IN 'ranking.py'

'search_priority' is used in 'quick_sort' function for sorting algorithm purposes

'''

import math
import re
import database # imports database functions, not variables
from database import client # client is global variable only to database.py

# -------------------------Search Function -----------------#

def quick_sort(items):
    '''
    Quicksort items based on book confidence
    Input:
        items: array of books with confidence values
    Output:

    '''
    if len(items) > 1:
        pivot_index = len(items) / 2
        smaller_items = []
        larger_items = []

        val = items[pivot_index]['search_priority'] # rating of the pivot item
        index = 0
        for i in items:
            # needs work, comment out if needed
            # sort based on items[index]['rating']
            if index != pivot_index:
                if i['search_priority'] < val:
                    smaller_items.append( i )
                else:
                    larger_items.append( i )
            index += 1

        quick_sort(smaller_items)
        quick_sort(larger_items)
        items[:] = smaller_items + [items[pivot_index]] + larger_items

def confidence( book ):
    '''
    Connects to database and returns confidence score for particular user w/ 'book'
    Based on the Wilson score interval

    Input:
        book (object in accounts-database)
    Output:
        confidence score for user (float))
    '''
    db = client['accounts-database']
    accounts = db['accounts']
    email = book['email']

    seller = accounts.find_one( {'email': email} )
    ups = seller['upvotes']
    downs = seller['downvotes']

    if ups + downs == 0:
        return 0
    else:
        return wilson_score_interval( ups, downs )

def wilson_score_interval( ups, downs ):
    '''
    Calculates the Wilson Score Interval given particular number
    of positive and negative votes
    Input:
        ups: number of positive votes (int)
        downs: number of negative votes (int)
    Output:
        Wilson confidence score

    Based on "How Reddit ranking algorithms work by Amir Salihefendic" on Medium:
    https://medium.com/hacking-and-gonzo/how-reddit-ranking-algorithms-work-ef111e33d0d9#.42jkgelwg
    '''
    n = ups + downs
    if n == 0:
        return 0

    z = 1.281551565545 # wilson constant
    p = float(ups) / n

    left = p + 1/(2*n)*z*z
    right = z * math.sqrt( p*(1-p) / n + z*z/ (4*n*n))
    under = 1+ 1/n *z*z

    return (left - right) / under


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
    for j in range(len(query)): #goes through query

        # goes through database to find books with query[j] in substring value
        cursor = books.find( {'bookName':
                              { '$regex' : '(?i).*' + query[j] + '.*' } } )
        for b in cursor:
            if not b in results:
                results.append( b )
                #break; #goes to next book

        cursor = books.find( {'author':
                      { '$regex' : '(?i).*' + query[j] + '.*' } } )
        for b in cursor:
            if not b in results:
                results.append( b )
                #break; #goes to next book

        cursor = books.find( {'isbn':
                              { '$regex' : '.*' + query[j] + '.*' } } )
        for b in cursor:
            if not b in results:
                results.append( b )
                #break; #goes to next book

    #deletes non-available entries
    results = [ book for book in results if book['status'] == 'available' ]

    # set confidence values for each user based on book
    # set's a book's rating based on user's current rating
    for i in results:
        user = database.getUser( i['email'] )
        currentRating = confidence( i )
        user['rating'] = currentRating
        i['search_priority'] = currentRating

    # sort results based on confidence values
    quick_sort( results )

    print results

    return results
