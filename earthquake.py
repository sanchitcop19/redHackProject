import json
content = None
with open("scored_output.json") as file:
    content = json.load(file)
from collections import defaultdict
store = defaultdict(int)
for con in content:
    store[con[-2:]] += (content[con]['disaster']['Earthquake_score'])
print(store)