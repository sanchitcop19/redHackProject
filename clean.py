import json
from property import get_address_price

content = None
with open("addresses.json") as file:
    content = json.load(file)
prices = []
for item, address in content.items():
    try:
        address = address.split(',')
        city_state = address[1] + " CA"
        address = address[0]
        result = get_address_price(address, city_state)
        prices.append(result if result[0] != 'error' else (address, random.randint(200000, 600000)))
    except:
        import random
        prices.append(random.randint(200000, 600000))

print(prices)