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
store = None
with open("scored_output.json") as file:
    store = json.load(file)

@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')

@app.route('/address', methods = ["POST"])
def process_address():
    county = request.form['county']
    state = request.form['state']
    address = request.form['address']
    """
    import googlemaps
    google_maps = googlemaps.Client(key='AIzaSyA3kdX2kwoRQpkmui8GtloGvGQB-rn1tMU')
    location = google_maps.geocode(address)

    # Loop through the first dictionary within `location` and find the address component that contains the 'administrative_area_level_2' designator, which is the county level
    target_string = 'administrative_area_level_2'
    for item in location[0]['address_components']:
        if target_string in item['types']:  # Match target_string
            county_name = item['long_name']  # Or 'short_name'
            break  # Break out once county is located
        else:
            # Some locations might not contain the expected information
            pass
    """

    # find score for county
    score = store[county + " , " + state]["score"]
    # find x neighboring counties

    # addresses in those neighboring counties
    return jsonify([county, state, address, score])

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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
