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
from property import get_address_price

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
    city = data['city']
    state = data['state']
    address = data['address']

    # find score for county
    location = county + " , " + state
    score = store[location]["score"]
    price = get_address_price(address, city + state)
    # find x neighboring counties, use the dmatrix
    from closest import closest_k
    closest_neighbors = closest_k(location)
    from collections import OrderedDict
    scores = OrderedDict()
    for neighbor in closest_neighbors:
        scores[neighbor] = store[neighbor]["score"]
    # query address for price
    price = get_address_price(address, city + " " + state)
    # query all closest_neighbors for price


    result = OrderedDict()
    result[address] = {
        "score": score,
        "price": price[1]
    }
    for neighbor, _score in zip(sorted(closest_neighbors, key=lambda x: scores[x]), scores.values()):
        result[neighbor] = {}
        result[neighbor]["score"] = _score
        result[neighbor]["price"] = 100000

    return jsonify(result)

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
