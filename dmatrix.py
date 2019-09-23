import requests
import json

content = None
with open("scored_output.json") as file:
    content = json.load(file)

matrix = [[0 for i in range(len(content))] for j in range(len(content))]
mapping = {}

for i, origin in enumerate(content):
    mapping[i] = origin
    for j, destination in enumerate(content):
        print(i, j)
        if origin[0] == ',' or destination[0] == ',' or origin[-2:] != destination[-2:] or origin[-2:] != 'CA':
            continue
        response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=" + origin + "&destinations=" + destination + "&key=" + "AIzaSyA3kdX2kwoRQpkmui8GtloGvGQB-rn1tMU")
        try:
            matrix[i][j] = json.loads(response.content)["rows"][0]["elements"][0]["distance"]["value"]
        except:
            continue
    data = {
        'mapping': mapping,
        'matrix': matrix
    }
    with open("dmatrix.json", "w") as file:
        json.dump(data, file)




