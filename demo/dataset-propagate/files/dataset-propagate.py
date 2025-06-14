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

def login(username, password, dremioServer):
  # we login using the old api for now
  loginData = {'userName': username, 'password': password}
  headers = {'content-type':'application/json'}
  response = requests.post('{server}/apiv2/login'.format(server=dremioServer), headers=headers, data=json.dumps(loginData))
  data = json.loads(response.text)
  # retrieve the login token
  token = data['token']
  return token

accesstoken_sandbox = login(sandbox_username, sandbox_password, sandbox_url)
accesstoken_production = login(prod_username,prod_password,prod_url)

def query(payload,env):
    if env == 'PROD':
        endpoint = prod_url
        token = accesstoken_production
    else:
        endpoint = sandbox_url
        token = accesstoken_sandbox
        
    response = requests.post(
        f"{endpoint}/api/v3/sql",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )   
        
    if response.status_code == 200:
        jobId = response.json().get("id")
        while True:
            response = requests.get(
                f"{endpoint}/api/v3/job/{jobId}",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == 200:
                jobStatus = response.json().get("jobState")
                if jobStatus == "COMPLETED":
                    result = requests.get(
                                    f"{endpoint}/api/v3/job/{jobId}/results",
                                    headers={"Authorization": f"Bearer {token}"},
                                )
                    rows = result.json().get("rows")
                    return rows
                if jobStatus == "CANCELED" or jobStatus == "FAILED":
                    return None
            else:  
                break
    else:
        print(f"Failed to get job details")
        return FileNotFoundError
        
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
    # db = request.args.get('db')
    view = request.args.get('view')
    schema = request.args.get('schema')
    count = request.args.get('count', type = str)

    if env == 'PROD':
        url = prod_url
        username = prod_username
        password = prod_password
    else:
        url = sandbox_url
        username = sandbox_username
        password = sandbox_password

    sql_str = f"""
                select 
                    *
                from 
                    "{schema}"."{view}"
                """
    if count is not None and count.isdigit():
        sql_str = sql_str + f" limit {count}"
    else:
        return jsonify({"message": "Parameter count is missing or not numeric."}), 401
    
    payload = {
        "sql": sql_str
    } 
    
    response = query(payload,None)

    if response is not None:
        response_json = json.dumps(response)
        return Response(response_json, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6005)

    
