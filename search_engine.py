
def searchForBook(query):
    '''
    Looks up a list book given a simple search query (no logical operators)
    Args:
        query (string)
    Returns:
        A list of books with that name/author
    '''
    db = client['books-database']
    books = db['books']

    #parse query to find relevant results
    results = []
    query = query.remove(',')
    query = query.split(' ')
    for i in range(books.count): #goes through book database
        for j in range(query.count): #goes through query
            if books[i]['bookName'].find(query[j]) != -1: #if found
                print 'book found, going to next book'
                results.append( books[i] )
                break; #goes to next book

    return results
