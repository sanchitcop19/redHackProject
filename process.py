import json
from collections import defaultdict
import pprint

#['disasterNumber', 'ihProgramDeclared', 'iaProgramDeclared', 'paProgramDeclared', 'hmProgramDeclared', 'state', 'declarationDate', 'fyDeclared', 'disasterType', 'incidentType', 'title', 'incidentBeginDate', 'incidentEndDate', 'disasterCloseOutDate', 'declaredCountyArea', 'placeCode', 'hash', 'lastRefresh']

def process(content):
    print(content)
    store = {}
    content = content[1:]
    for line in content:
        county = line[14]
        disaster = line[9]
        if county:
            store[county] = {}
            store[county]["disaster"] = defaultdict(int)
    for line in content:
        county = line[14]
        disaster = line[9]
        if county:
            store[county]["disaster"][disaster] += 1

    pprint.pprint(store, indent=4)
    print(len(store))

content = None
with open("output.json") as file:
    content = json.load(file)
process(content)