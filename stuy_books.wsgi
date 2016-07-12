#!/usr/bin/python
activate_this = '/var/www/stuy_books/stuy_books/venv/bin/activate_this.py'
execfile( activate_this, dict(__file__=activate_this ))

import sys, logging
logging.basicConfig(stream=sys.stderr)

sys.path.insert(0,"/var/www/stuy_books")

from stuy_books import app as application
#import app as application
application.secret_key = 'Add your secret key'
