import json
from collections import defaultdict
from datetime import datetime
import pprint

#['disasterNumber', 'ihProgramDeclared', 'iaProgramDeclared', 'paProgramDeclared', 'hmProgramDeclared', 'state', 'declarationDate', 'fyDeclared', 'disasterType', 'incidentType', 'title', 'incidentBeginDate', 'incidentEndDate', 'disasterCloseOutDate', 'declaredCountyArea', 'placeCode', 'hash', 'lastRefresh']

def process(content):
    def score(county, disaster):
        county_data = store[county]["disaster"]
        frequency_score = county_data[disaster]["frequency"]/max_values[disaster]["max"]
        duration_score = 0
        if county_data[disaster]["frequency"]>0:
            duration_score = store[county]["disaster"][disaster]["average_duration"]/longest_duration[disaster]["duration"]
        return frequency_score*70+duration_score*60
    max_values = defaultdict(lambda: {"county": "", "max": 0})
    longest_duration = defaultdict(lambda: {"county": "", "duration": 0})
    max_scores = defaultdict(lambda: {"county": "", "score": 0})
    store = {}
    content = content[1:]
        
    for line in content:
        state  = line[5]
        county = line[14].split('(')[0] + ", " + state
        disaster = line[9]
        if county==", ":
            continue
        if county not in store:
             store[county] = {}
             store[county]["disaster"] = defaultdict(lambda: {"frequency": 0, "total_duration": 0, "disaster_with_date": 0})
        else:
            if line[12] and line[13]:
                begin_date = datetime.strptime(line[11][:10], "%Y-%m-%d")
                end_date = datetime.strptime(line[12][:10], "%Y-%m-%d")
            if county:
                store[county]["disaster"][disaster]["frequency"] += 1
                if begin_date and end_date:
                    store[county]["disaster"][disaster]["total_duration"] +=  (end_date-begin_date).days
                    store[county]["disaster"][disaster]["disaster_with_date"]+=1
    for county in store:
        county_data = store[county]["disaster"]
        for disaster in county_data:
            county_data[disaster]["average_duration"] = county_data[disaster]["total_duration"]/store[county]["disaster"][disaster]["disaster_with_date"]
            if max_values[disaster]["max"] < county_data[disaster]["frequency"]:
                max_values[disaster] = {"max":county_data[disaster]["frequency"], "county": county}
            if longest_duration[disaster]["duration"] < county_data[disaster]["average_duration"]:
                longest_duration[disaster] = {"duration": county_data[disaster]["average_duration"], "county": county}
    for county in store:
        county_data = store[county]["disaster"]
        num_scores = 0
        current_score = 0
        for disaster in ["Fire", "Hurricane", "Tornado", "Flood", "Earthquake", "Snow"]:
            county_data[disaster+"_score"] = score(county, disaster)
            if county_data[disaster + "_score"]:
                current_score += county_data[disaster+"_score"]
                num_scores += 1
            if county_data[disaster+"_score"]> max_scores[disaster]["score"]:
                max_scores[disaster] = {"county": county, "score": county_data[disaster+"_score"]}
        store[county]["score"] = (current_score / (num_scores if num_scores else 1))

    max_score = max([store[county]["score"] for county in store])
    for county in store:
        store[county]["score"] /= max_score
        store[county]["score"] *= 100

    with open("scored_output.json", "w") as file:
        json.dump(store, file, indent=4)



    
    #pprint.pprint(store, indent=4)
    # pprint.pprint(longest_duration, indent=4)
    pprint.pprint(max_scores, indent=4)

content = None
with open("output.json") as file:
    content = json.load(file)
process(content)