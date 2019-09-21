#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, jsonify
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import os
import json

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
store, dmatrix = None, None
with open("scored_output.json") as file:
    store = json.load(file)
with open("dmatrixca.json") as file:
    dmatrix = json.load(file)

@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')

@app.route('/address', methods = ["POST"])
def process_address():
    data = json.loads(request.data)
    county = data['county']
    state = data['state']
    address = data['address']

    # find score for county
    location = county + " , " + state
    score = store[location]["score"]
    # find x neighboring counties, use the dmatrix
    from closest import closest_k
    closest_neighbors = closest_k(location)
    scores = [store[neighbor]["score"] for neighbor in closest_neighbors]
    # query address for price
    # query all closest_neighbors for price
    result = {
        address:
    }
    price = 500
    return jsonify([address, price, score, county, state]*10)

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    import os
    print(os.getcwd())
    app.run(port = 5002)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
