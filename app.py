#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, jsonify
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
import os
import requests 
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

@app.route('/earthquake', methods=["POST"])
def determine_earthquake():
    data = json.loads(request.data)
    
    longitude = float(data["longitude"])
    latitude = float(data["latitude"])
    min_latitude =  -0.45+ latitude
    max_latitude = 0.45+ latitude
    min_longitude = -.4 + longitude
    max_longitude = .4+longitude
    response = requests.get("https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=1980-01-01&endtime=2000-01-02&maxlatitude={}&minlatitude={}&maxlongitude={}&minlongitude={}".format(max_latitude, min_latitude, max_longitude, min_longitude))
    #print("https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=1980-01-01&endtime=2000-01-02&maxlatitude={}&minlatitude={}&maxlongitude={}&minlongitude={}".format(max_latitude, min_latitude, max_longitude, min_longitude))
    response = response.json()
    x_vector = [0]*5
    for data in response["features"]:
        data = data["properties"]
        if not data['mag']:
            continue
        if 4.5 < data["mag"] <5:
            x_vector[0]+=1
        elif 5 < data["mag"] <5.5:
            x_vector[1]+=1
        elif 5.5 < data["mag"] <6:
            x_vector[2]+=1
        elif 6 < data["mag"] < 6.5:
            x_vector[3]+=1
        elif data["mag"]>6.5:
            x_vector[4]+=1
    ml_instance_id = "f84688e7-0454-4ca1-a25c-1af2172e6772"
    iam_token = "eyJraWQiOiIyMDE5MDUxMyIsImFsZyI6IlJTMjU2In0.eyJpYW1faWQiOiJpYW0tU2VydmljZUlkLWU5YWVlYzhmLTNiOTQtNDQ5NC04ZTE0LTI1YjdiNDAzZDg3MiIsImlkIjoiaWFtLVNlcnZpY2VJZC1lOWFlZWM4Zi0zYjk0LTQ0OTQtOGUxNC0yNWI3YjQwM2Q4NzIiLCJyZWFsbWlkIjoiaWFtIiwiaWRlbnRpZmllciI6IlNlcnZpY2VJZC1lOWFlZWM4Zi0zYjk0LTQ0OTQtOGUxNC0yNWI3YjQwM2Q4NzIiLCJzdWIiOiJTZXJ2aWNlSWQtZTlhZWVjOGYtM2I5NC00NDk0LThlMTQtMjViN2I0MDNkODcyIiwic3ViX3R5cGUiOiJTZXJ2aWNlSWQiLCJhY2NvdW50Ijp7InZhbGlkIjp0cnVlLCJic3MiOiI3NjE4ZGJlNjcxYzY0OTk3YmU3ZTkzMzU3Zjg3NjEzMyJ9LCJpYXQiOjE1NjkxMTEzNTcsImV4cCI6MTU2OTExNDk1NywiaXNzIjoiaHR0cHM6Ly9pYW0ubmcuYmx1ZW1peC5uZXQvb2lkYy90b2tlbiIsImdyYW50X3R5cGUiOiJ1cm46aWJtOnBhcmFtczpvYXV0aDpncmFudC10eXBlOmFwaWtleSIsInNjb3BlIjoiaWJtIG9wZW5pZCIsImNsaWVudF9pZCI6ImJ4IiwiYWNyIjoxLCJhbXIiOlsicHdkIl19.Ebiu1ISGAHEdV48HGN_ByTgXNkXC_PZ-JsnxoawIGB_zwF307CGMTfZ3WnuSl1A3Xs00KF-0oy5xVZ1iVPaduEorEgjY0gvzXGcA3UPXkaBQ8lqFsERUJgNRVkdOm5XbhYgsl2uSRsPNLj9px1gy9hsUnyYQpcKl6ywwnmIr3KHYzB1WQCOMiMEcQ-aAikjRVDYtNmjoWQf6NGG23r7rpl2bb4c2g_-q0-XehAuK_uBaDbZd1rAVdkgV7ac1-84cwjNmXNZ-7vOMWpFywgUSIlhBkt-TWJPCU8-5_lrmf6hwKJqDfefDyLCtjO30Iv1Lk29iuYPM_xBJqCVfG67rxQ"
    # NOTE: generate iam_token and retrieve ml_instance_id based on provided documentation	
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + iam_token, 'ML-Instance-ID': ml_instance_id}
    
    # NOTE: manually define and pass the array(s) of values to be scored in the next line
    payload_scoring = {"input_data": [{"fields": ["0", "1", "2", "3", "4"], "values": [x_vector]}]}

    response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/v4/deployments/d7f03c4c-86a4-44b0-a286-355c9315d701/predictions', json=payload_scoring, headers=header)
    return str(json.loads(response_scoring.text)["predictions"][0]["values"][0][0])

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
    # result = {
    #     address:
    # }
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
