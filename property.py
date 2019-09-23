import requests
import untangle

address = "2 sweethome road"
city_state = "Buffalo NY"


def get_address_price(address, city_state):
    z_id = "X1-ZWz17nn6wywbnv_17jma"
    base_url = f"http://www.zillow.com/webservice/GetSearchResults.htm?zws-id={z_id}&address={address}&citystatezip={city_state}"
    res = requests.get(base_url)
    result = res.text
    obj = untangle.parse(result)
    search_result = obj.SearchResults_searchresults
    error = int(search_result.message.code.cdata) != 0
    if error:
        return search_result.message.text.cdata
    else:
        prices = search_result.response.results.result
        if isinstance(prices, list):
            price = prices[0].zestimate.amount.cdata
            street = prices[0].address.street.cdata
        else:
            price = prices.zestimate.amount.cdata
            street = prices.address.street.cdata
        if len(price) is 0:
            price = "0"
        return (street, int(price))
