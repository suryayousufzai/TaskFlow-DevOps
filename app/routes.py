# app/routes.py
# this file handles the actual web page routes (the ones that return HTML)
# i kept it separate from api.py because those return JSON, not pages
# this way it's easier to find things

from flask import Blueprint, render_template, jsonify

# a blueprint is just a way to group related routes
# i register this in __init__.py
main = Blueprint('main', __name__)


# GET /
# serves the main page - that's it
# all the data on the page is loaded by javascript after the page loads
# so this route doesn't need to do much
@main.route('/')
def index():
    return render_template('index.html')


# GET /health
# used by docker to check if the app is alive
# also useful to quickly test if the server is running
@main.route('/health')
def health():
    return jsonify({'status': 'ok'})
