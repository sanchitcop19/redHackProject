def get_token():
    import requests
    apikey = "_2sIrXpDMRQadByPZIWznTx7KdrxbIhj4GIA7qoNV1Rr"
    url     = "https://iam.bluemix.net/oidc/token"
    headers = { "Content-Type" : "application/x-www-form-urlencoded" }
    data    = "apikey=" + apikey + "&grant_type=urn:ibm:params:oauth:grant-type:apikey"
    IBM_cloud_IAM_uid = "bx"
    IBM_cloud_IAM_pwd = "bx"
    response  = requests.post( url, headers=headers, data=data, auth=( IBM_cloud_IAM_uid, IBM_cloud_IAM_pwd ) )

    iam_token = response.json()["access_token"]
    return iam_token
