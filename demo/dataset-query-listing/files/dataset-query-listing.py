from flask import Flask, request, jsonify
import requests
import logging
import os
import json

app = Flask(__name__)
sandbox_endpoint = os.environ['SANDBOX_URL']
prod_endpoint = os.environ['PROD_URL']
sandbox_usr = os.environ['SANDBOX_USERNAME']
sandbox_pw = os.environ['SANDBOX_PASSWORD']
prod_usr = os.environ['PROD_USERNAME']
prod_pw = os.environ['PROD_PASSWORD']

def login(username, password, dremioServer):
  # we login using the old api for now
  loginData = {'userName': username, 'password': password}
  headers = {'content-type':'application/json'}
  response = requests.post('{server}/apiv2/login'.format(server=dremioServer), headers=headers, data=json.dumps(loginData))
  data = json.loads(response.text)
  # retrieve the login token
  token = data['token']
  return token

accesstoken_sandbox = login(sandbox_usr, sandbox_pw, sandbox_endpoint)
accesstoken_production = login(prod_usr,prod_pw,prod_endpoint)

def get_dataset_desc(catalog, dataset_path,name,env):
    payload = {
        "sql": f"""
                select 
                    COLUMN_NAME
                    ,IS_NULLABLE
                    ,DATA_TYPE
                from 
                    INFORMATION_SCHEMA.COLUMNS c
                where
                    c.TABLE_CATALOG = '{catalog}'
                    and c.TABLE_SCHEMA = '{dataset_path}'
                    and c.TABLE_NAME = '{name}'
                """
    }   
    return query(payload,None)

def query(payload,env):
    if env == 'PROD':
        endpoint = prod_endpoint
        token = accesstoken_production
    else:
        endpoint = sandbox_endpoint
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
    
def get_dataset_metadata(env):
    payload = {
        "sql": """
                select 
                    v.TABLE_SCHEMA
                    ,v.TABLE_NAME
                    ,v.VIEW_DEFINITION
                    ,v.TABLE_CATALOG
                from 
                    INFORMATION_SCHEMA.VIEWS v
                """
    }
    return query(payload,None)



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

@app.route('/listalldatasets', methods=['GET'])
def ListAllDatasets():
    logging.info('ListAllDatasets function processed a request.')
    env = request.args.get('env')    
    return jsonify(get_dataset_metadata(env))

@app.route('/showdatasetdesc', methods=['GET'])
def ShowDatasetDesc():
    logging.info('ShowDatasetDesc function processed a request.')
    name = request.args.get('name')
    path = request.args.get('path')
    catalog = request.args.get('catalog')
    env = request.args.get('env')

    if name:
        result = get_dataset_desc(catalog,path,name,env)
        if result is not None:
            return jsonify(result)
        else:
            return jsonify({"error": "Failed to retrieve dataset description"}), 500
    else:
        return jsonify({"message": "No name parameter provided"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)

    