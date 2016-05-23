from oauth2client.client import OAuth2WebServerFlow
import httplib2
from oauth2client.file import Storage

#from apiclient.discovery import build

flow = OAuth2WebServerFlow(client_id='546971034348-fflcn8cq3l3g5a9od0dnorlbgckrquuo.apps.googleusercontent.com',
                           client_secret='glyj32qfvGD8b7zOXVElbMOX',
                           scope='profile email'
                           redirect_uri='https://localhost:8000')

auth_uri = flow.step1_get_authorize_url()
code = flow.step1_get_device_and_user_codes()

credentials = flow.step2_exchange(code)

http = httplib2.Http()
http = credentials.authorize(http)

storage = Storage("cred.txt")
storage.put(credentials)

credentials = store.get()

print credentials

import json

import flask
import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client.client import OAuth2WebServerFlow


app = Flask(__name__)

@app.route('/google')
def googleLogin():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
        if credentials.access_token_expired:
            return flask.redirect(flask.url_for('oauth2callback'))
        else:
            flask.redirect(flask.url_for("index"))
            #http_auth = credentials.authorize(httplib2.Http())
            #drive_service = discovery.build('drive', 'v2', http_auth)
            #files = drive_service.files().list().execute()
            #return json.dumps(files)

@app.route('/oauth2callback')
def oauth2callback():
    flow = OAuth2WebServerFlow(client_id='546971034348-fflcn8cq3l3g5a9od0dnorlbgckrquuo.apps.googleusercontent.com',
                               client_secret='glyj32qfvGD8b7zOXVElbMOX',
                               scope='profile email',
                               redirect_uri='https://localhost:8000')
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('google'))
        
