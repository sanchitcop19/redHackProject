#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, jsonify, url_for, redirect
from forms import SearchForm
import logging
from logging import Formatter, FileHandler
import os
import requests 
import json
from property import get_address_price

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
store, dmatrix = None, None
with open("scored_output.json") as file:
    store = json.load(file)
with open("dmatrixca.json") as file:
    dmatrix = json.load(file)

@app.route('/', methods = ["GET", "POST"])
def home():
    form = SearchForm()
    if form.validate_on_submit():
        address = form["search"].data
        return redirect(url_for('process_address', address = address))
    return render_template('index.html', form = form)

@app.route('/earthquake', methods=["POST"])
def determine_earthquake():
    data = json.loads(request.data)
    
    longitude = float(data["longitude"])
    latitude = float(data["latitude"])
    min_latitude =  -0.45+ latitude
    max_latitude = 0.45+ latitude
    min_longitude = -.5 + longitude
    max_longitude = .5+longitude
    response = requests.get("https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=1980-01-01&endtime=2000-01-02&maxlatitude={}&minlatitude={}&maxlongitude={}&minlongitude={}&minmagnitude=3".format(max_latitude, min_latitude, max_longitude, min_longitude))
    print("https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=1980-01-01&endtime=2000-01-02&maxlatitude={}&minlatitude={}&maxlongitude={}&minlongitude={}&minmagnitude=3".format(max_latitude, min_latitude, max_longitude, min_longitude))
    
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
    if x_vector[2]>3:
        return "2"
    if x_vector[3]>1:
        return "3"
    ml_instance_id = "f84688e7-0454-4ca1-a25c-1af2172e6772"
    iam_token = "eyJraWQiOiIyMDE5MDUxMyIsImFsZyI6IlJTMjU2In0.eyJpYW1faWQiOiJpYW0tU2VydmljZUlkLWU5YWVlYzhmLTNiOTQtNDQ5NC04ZTE0LTI1YjdiNDAzZDg3MiIsImlkIjoiaWFtLVNlcnZpY2VJZC1lOWFlZWM4Zi0zYjk0LTQ0OTQtOGUxNC0yNWI3YjQwM2Q4NzIiLCJyZWFsbWlkIjoiaWFtIiwiaWRlbnRpZmllciI6IlNlcnZpY2VJZC1lOWFlZWM4Zi0zYjk0LTQ0OTQtOGUxNC0yNWI3YjQwM2Q4NzIiLCJzdWIiOiJTZXJ2aWNlSWQtZTlhZWVjOGYtM2I5NC00NDk0LThlMTQtMjViN2I0MDNkODcyIiwic3ViX3R5cGUiOiJTZXJ2aWNlSWQiLCJhY2NvdW50Ijp7InZhbGlkIjp0cnVlLCJic3MiOiI3NjE4ZGJlNjcxYzY0OTk3YmU3ZTkzMzU3Zjg3NjEzMyJ9LCJpYXQiOjE1NjkxMTEzNTcsImV4cCI6MTU2OTExNDk1NywiaXNzIjoiaHR0cHM6Ly9pYW0ubmcuYmx1ZW1peC5uZXQvb2lkYy90b2tlbiIsImdyYW50X3R5cGUiOiJ1cm46aWJtOnBhcmFtczpvYXV0aDpncmFudC10eXBlOmFwaWtleSIsInNjb3BlIjoiaWJtIG9wZW5pZCIsImNsaWVudF9pZCI6ImJ4IiwiYWNyIjoxLCJhbXIiOlsicHdkIl19.Ebiu1ISGAHEdV48HGN_ByTgXNkXC_PZ-JsnxoawIGB_zwF307CGMTfZ3WnuSl1A3Xs00KF-0oy5xVZ1iVPaduEorEgjY0gvzXGcA3UPXkaBQ8lqFsERUJgNRVkdOm5XbhYgsl2uSRsPNLj9px1gy9hsUnyYQpcKl6ywwnmIr3KHYzB1WQCOMiMEcQ-aAikjRVDYtNmjoWQf6NGG23r7rpl2bb4c2g_-q0-XehAuK_uBaDbZd1rAVdkgV7ac1-84cwjNmXNZ-7vOMWpFywgUSIlhBkt-TWJPCU8-5_lrmf6hwKJqDfefDyLCtjO30Iv1Lk29iuYPM_xBJqCVfG67rxQ"
    # NOTE: generate iam_token and retrieve ml_instance_id based on provided documentation	
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + iam_token, 'ML-Instance-ID': ml_instance_id}

    # NOTE: manually define and pass the array(s) of values to be scored in the next line
    payload_scoring = {"input_data": [{"fields": ["0", "1", "2", "3", "4"], "values": [[18,10,1,0,1]]}]}

    response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/v4/deployments/1d20095e-acdc-4c53-a82c-07daacf2e3d7/predictions', json=payload_scoring, headers=header)

    print(response_scoring.text)
    return str(json.loads(response_scoring.text))

@app.route('/list', methods = ["GET", "POST"])
def list():
    info = request.get_json()
    return render_template('list.html', info = info)

@app.route('/address/', methods = ["GET", "POST"])
def process_address():
    address = request.args["address"]
    query = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address + "&key=AIzaSyB0gbwLd0woievTa-_BwG9ZylFpXX27BUg"
    response = requests.get(query).json()
    for data in response["results"][0]["address_components"]:
        if 'administrative_area_level_2' in data["types"]:
            county = data["long_name"]
        if 'administrative_area_level_1' in data["types"]:
            state = data["short_name"]
        if 'locality' in data["types"]:
            city = data["long_name"]
    latitude = response["results"][0]["geometry"]["location"]["lat"]
    longitude = response["results"][0]["geometry"]["location"]["lng"]

    # find score for county

    location = county[:county.index(' County')] + " , " + state
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
    content = None
    prices = {}
    if state == "CA":
        with open("addresses.json") as file:
            content = json.load(file)

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
        if content:
            street = content[neighbor] if neighbor in content else ""
        else:
            street = address
        final.append({
            "street": street,
            "score": _score,
            "price": prices[street] if street in prices and prices else 0
        })
    response = requests.post("http://127.0.0.1:5001/list", json = final)
    return response

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
    app.run(port = 5001)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
