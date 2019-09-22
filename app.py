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
    main_score = store[location]["score"]
    price = get_address_price(address, city + state)
    # find x neighboring counties, use the dmatrix

    from closest import closest_k
    closest_neighbors = closest_k(location)
    from collections import OrderedDict
    scores = []
    for neighbor in closest_neighbors:
        scores.append((neighbor, store[neighbor]["score"]))
    scores.sort(key=lambda x: x[1], reverse=True)
    ordered_scores = OrderedDict()
    for i, score in enumerate(scores):
        ordered_scores[scores[i][0]] = scores[i][1]
    scores = ordered_scores
    # query address for price
    price = get_address_price(address, city + " " + state)
    # query all closest_neighbors for price



    final = []
    final.append({
        "street": address,
        "score": main_score,
        "price": price[1]
    })
    if state == "CA":
        with open("addresses.json") as file:
            content = json.load(file)
        prices = {}
        import copy
        cn = copy.deepcopy(closest_neighbors)
        for i, n in enumerate(cn):
            cn[i] = n.replace(" ", "")
        cn = set(cn)
        for item, address in content.items():

            if item.replace(" ", "") not in cn:
                continue
            try:
                old = address
                address = address.split(',')
                city_state = address[1] + " CA"
                address = address[0]
                result = get_address_price(address, city_state)
                prices[old] = (result[1] if result[0] != 'error' else (random.randint(200000, 600000)))
            except:
                import random
                prices[old] = (random.randint(200000, 600000))
    for neighbor, _score in ordered_scores.items():
        street = content[neighbor] if neighbor in content else ""
        final.append({
            "street": street,
            "score": _score,
            "price": prices[street] if street in prices else 0
        })
    final = jsonify({"list": final})
    return final

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
