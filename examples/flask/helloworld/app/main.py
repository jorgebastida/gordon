import awsgi
import json
from flask import Flask, url_for

with open('.context', 'r') as f:
    gordon_context = json.loads(f.read())

app = Flask(__name__)

@app.route('/')
def index():
    return 'hello world! <a href="%s">foo</a>' % url_for('foo'), 200

@app.route('/foo')
def foo():
    return 'baaaaa!', 200

# The app is mounted on '/dev' (or whatever) and we want to
# fixup the generated URLs.  Based on:
# https://gist.github.com/Larivact/1ee3bad0e53b2e2c4e40
class FixScriptName(object):
    def __init__(self, app, script_name):
        self.app = app
        self.script_name = script_name

    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = self.script_name
        return self.app(environ, start_response)

app = FixScriptName(app, gordon_context['script_name'])

def lambda_handler(event, context):
    return awsgi.response(app, event, context)
