from flask import Flask, request, jsonify, Response
import requests
import logging
import os
from requests.auth import HTTPBasicAuth
import json

app = Flask(__name__)
sandbox_url = os.environ['SANDBOX_URL']
prod_url = os.environ['PROD_URL']
sandbox_username = os.environ['SANDBOX_USERNAME']
sandbox_password = os.environ['SANDBOX_PASSWORD']
prod_username = os.environ['PROD_USERNAME']
prod_password = os.environ['PROD_PASSWORD']

@app.after_request
def after_request(response):
    # Only add CORS headers if the Origin header exists and is from localhost
    origin = request.headers.get('Origin')
    if origin and 'localhost' in origin:
        # Add CORS headers to the response
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/datapropagate', methods=['GET'])
def PropagateDatasets():
    logging.info('PropagateDatasets function processed a request.')
    env = request.args.get('env')
    db = request.args.get('db')
    view = request.args.get('view')
    count = request.args.get('count', type = str)

    if env == 'PROD':
        url = prod_url
        username = prod_username
        password = prod_password
    else:
        url = sandbox_url
        username = sandbox_username
        password = sandbox_password

    if count is None:
        params = {
            '$format': 'json'
        }
    elif count.isdigit():
        params = {
            '$format': 'json'
            ,'$count': count
        }
    else:
        return jsonify({"message": "Parameter count is missing or not numeric."}), 401

    if db:
        response = requests.get(
            f"{url}/{db}/views/{view}",
            auth=HTTPBasicAuth(username, password),
            params=params
        )
    
    else:
        return jsonify({"message": "No db parameter provided"}), 400


    if response.status_code == 200:
        response_json = response.json()
        data_rows = response_json['elements']
        for data in data_rows:
            data.pop('links', None)
        json_data = json.dumps(data_rows)
    else:
        print(f"Failed to get metadata for dataset: {response.content}")

    # return json.dumps(data_rows)
    return Response(json_data, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6005)

    
