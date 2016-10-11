'''
Authors: Samuel Zhang
Description: Scrapes Google Images for image urls

------------------------------------
IMAGE SYSTEM DESIGN NOTES:

All images are URLs that link to that image for use in front end.

All auto-generated images are marked as "unapproved".

All "unapproved" will be checked by system administration to prevent abuse.

Once verified, an image will be marked as "approved".

All "approved" images will be used for the same request in the future.

'''

from pymongo import MongoClient

from bs4 import BeautifulSoup
import urllib2
import re

global stockImageUrl
stockImageUrl = ''

client = MongoClient()

#------------------------- Image Database -------------------------#
def getApprovedImageUrls():
    '''
    Gets approved image urls
    Args:
        None
    Returns:
        list of image urls
    '''
    db = client['books-database']
    images = db['images']
    result = images.find({'status': 'approved'})
    urls = []
    for r in result:
        urls.append(r['image_url'])
    return urls

def getUnapprovedImageUrls():
    '''
    Gets unapproved image urls
    Args:
        None
    Returns:
        list of image urls
    '''
    db = client['books-database']
    images = db['images']
    result = images.find({'status': 'unapproved'})
    urls = []
    for r in result:
        urls.append(r['image_url'])
    return urls    

def addImageUrl(url, status='unapproved'):
    '''
    Adds a url to the image collection
    Args:
        url
    Returns:
        True
    '''
    db = client['books-database']
    images = db['images']
    result = images.find_one({'image_url': url, 'status': status})
    if result == None:
        images.insert_one({'image_url': url, 'status': status })
    return True

def changeImageStatus(url, oldStatus ,status):
    '''
    Sets the status of an image (default: 'approved')
    Args:
        status (string)
    Returns:
        True
    '''
    db = client['books-database']
    images = db['images']
    if status == 'approved':
        db.find_one_and_update(
            {'image_url': url, 'status': oldStatus},
            {'$set': {'status': status}}
        )
    return True

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
        url (string) if approved
        stockImageUrl (string) if not approved
    '''
    query = query.split()
    query = '+'.join(query)
    url = "https://www.google.co.in/search?q="+query+"&source=lnms&tbm=isch"
    header = {'User-Agent': 'Mozilla/5.0'}
    soup = get_soup(url,header)

    images = [a['src'] for a in soup.find_all("img", {"src": re.compile("gstatic.com")})]
    for i in images:
        i = str(") + i + str(")

    # If stockImageUrl doesn't exist, make it
    if 'stockImageUrl' not in globals():
        global stockImageUrl # declared at top of image.py, but just in case
        stockImageUrl = ''
        
    #This is called once, then stockImageUrl will be permanent
    if stockImageUrl == '':
        stockurl = "https://www.google.co.in/search?q=pending&source=lnms&tbm=isch"
        stockheader = {'User-Agent': 'Mozilla/5.0'}
        stocksoup = get_soup(stockurl,stockheader)

        stockimages = [a['src'] for a in stocksoup.find_all("img", {"src": re.compile("gstatic.com")})]
        for j in stockimages:
            j = str(") + j + str(")
        stockImageUrl = stockimages[0]

    #for second choice, return images[1], etc.
    approvedImages = getApprovedImageUrls()

    if images[0] in approvedImages:
        return images[0]
    addImageUrl(images[0]) # add image url with 'unapproved' status
    return stockImageUrl

