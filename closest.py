def closest_k(location):
    import json
    content = None
    with open("dmatrixca.json") as file:
        content = json.load(file)

    matrix = content['matrix']
    mapping = content['mapping']
    reverse_mapping = {v: k for k, v in mapping.items()}
    ids = [id for id, map in mapping.items() if "CA" in map and map[0] != ',']

    # given county, find index of county in matrix
    # go through all it's neighbors and find the one with min distance
    index = reverse_mapping[location]
    state = location[-2:]
    neighbors = [(matrix[int(index)][int(id)], id) for id, map in mapping.items() if state in map and map[0] != ',']
    import heapq
    heapq.heapify(neighbors)
    closest_neighbors = heapq.nsmallest(11, neighbors)[1:]
    return [mapping[neighbor[1]] for neighbor in closest_neighbors]

if __name__ == '__main__':
    print(closest_k('Alpine , CA'))