# app/routes.py
# Main page routes - handles the HTML page requests
# The actual data routes are in api.py

from flask import Blueprint, render_template, jsonify

# create a blueprint to group these routes together
main = Blueprint('main', __name__)


@main.route('/')
def index():
    # just serve the main HTML page
    # all the data loading is handled by JavaScript on the frontend
    return render_template('index.html')


@main.route('/health')
def health():
    # simple health check endpoint
    # used by Docker and monitoring tools to check if the app is running
    return jsonify({'status': 'ok'})
