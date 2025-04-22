from flask import Flask, request, jsonify
import requests
import logging
import os
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import json
import psycopg2 as dbdriver
import re

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

@app.route('/listalldatasets', methods=['GET'])
def ListAllDatasets():
    logging.info('ListAllDatasets function processed a request.')
    env = request.args.get('env')
    db = request.args.get('db')
    if env == 'PROD':
        url = prod_url
        username = prod_username
        password = prod_password
    else:
        url = sandbox_url
        username = sandbox_username
        password = sandbox_password

    params = {
        '$format': 'json'
    }

    if db:
        response = requests.get(
            f"{url}/{db}",
            auth=HTTPBasicAuth(username, password),
            params=params
        )
        

    else:
        return jsonify({"message": "No db parameter provided"}), 400


    if response.status_code == 200:
        response_json = response.json()
        view_list = response_json['views-metadata']
        catalog_names = [item['name'] for item in view_list]
    else:
        print(f"Failed to get metadata for dataset: {response.content}")

    return jsonify(catalog_names)

@app.route('/showdatasetdesc', methods=['GET'])
def ShowDatasetDesc():
    logging.info('ShowDatasetDesc function processed a request.')
    name = request.args.get('name')
    db = request.args.get('db')

    if name and db:
        env = request.args.get('env')
        if env == 'PROD':
            url = prod_url
            username = prod_username
            password = prod_password
        else:
            url = sandbox_url
            username = sandbox_username
            password = sandbox_password

        params = {
            '$format': 'json'
        }

        response = requests.get(
            f"{url}/{db}/views/{name}/$schema",
            auth=HTTPBasicAuth(username, password),
            params=params
        )

        if response is not None:
            data = response.json()
            # Extract the "properties" dictionary
            properties = data.get("properties", {})

            # Transform the "properties" dictionary into the desired list of dictionaries
            result = [{"name": key, "type": value["type"]} for key, value in properties.items()]
            return result
        else:
            return jsonify({"error": "Failed to retrieve dataset description"}), 500
    else:
        return jsonify({"message": "No name or db parameter provided"}), 400


def check_access(user, dataset_name):
    denodoserver_name = "denodo-denodo-platform-service.denodo-ns"

    ## Default port for ODBC connections
    denodoserver_odbc_port = "9996"
    denodoserver_database = "admin"
    denodoserver_uid = "admin"
    denodoserver_pwd = "admin"

    ## Establishing a connection
    cnxn = dbdriver.connect(
        dbname=denodoserver_database,
        user=denodoserver_uid,
        password=denodoserver_pwd,
        host=denodoserver_name,
        port=denodoserver_odbc_port,
    )

    query = f"desc vql view {dataset_name} ('includeUserPrivileges' = 'yes')"
    cur = cnxn.cursor()
    cur.execute(query)
    results = cur.fetchall()
    dataset_description = results[0][0]
    user_privileges = "# #######################################\n# USER PRIVILEGES\n# #######################################\n"
    role_privileges = "# #######################################\n# ROLE PRIVILEGES\n# #######################################\n"
    idx1 = dataset_description.find(user_privileges)
    idx2 = dataset_description.find(role_privileges)
    users = dataset_description[idx1+len(user_privileges):idx2]
    users = re.findall("ALTER USER (\w*)", users)

    return user in users


@app.route('/check-user-access', methods=['GET'])
def check_user_access():
    user = request.args.get("username")

    denodoserver_name = "denodo-denodo-platform-service.denodo-ns"

    ## Default port for ODBC connections
    denodoserver_odbc_port = "9996"
    denodoserver_database = "admin"
    denodoserver_uid = "admin"
    denodoserver_pwd = "admin"

    ## Establishing a connection
    cnxn = dbdriver.connect(
        dbname=denodoserver_database,
        user=denodoserver_uid,
        password=denodoserver_pwd,
        host=denodoserver_name,
        port=denodoserver_odbc_port,
    )

    query = f"list views base"
    cur = cnxn.cursor()
    cur.execute(query)
    results = cur.fetchall()
    views = [view for row in results for view in row]
    datasets_access = []
    for view in views:
        if check_access(user, view):
            datasets_access.append(view)

    return datasets_access


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)

    
