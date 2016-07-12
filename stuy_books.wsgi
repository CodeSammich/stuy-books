'''
If in /var/www on Apache-based server with proper stuy_books.conf configuration,
place in directory above repo

/var/www/stuy_books/stuy_books = repo directory
/var/www/stuy_books = .wsgi directory

For more information, visit: https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
'''

#!/usr/bin/python
activate_this = '/var/www/stuy_books/stuy_books/venv/bin/activate_this.py'
execfile( activate_this, dict(__file__=activate_this ))

import sys, logging
logging.basicConfig(stream=sys.stderr)

sys.path.insert(0,"/var/www/stuy_books")

from stuy_books import app as application
#import app as application
application.secret_key = 'Add your secret key'
