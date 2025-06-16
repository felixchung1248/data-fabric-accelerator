from flask import Flask, request, jsonify
import requests
import logging
import os
from requests.auth import HTTPBasicAuth
import json
import psycopg2 as dbdriver
import re

app = Flask(__name__)
url = os.environ['ZAMMAD_URL']
username = os.environ['ZAMMAD_USR']
password = os.environ['ZAMMAD_PW']
jenkins_wrapper_url = os.environ['JENKINS_WRAPPER_URL']


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

@app.route('/approveticket', methods=['PUT'])
def ApproveTicket():
    ticket_id = request.args.get('ticketId', default=None)
    dataset_name = request.args.get('datasetName', default=None)
    dataset_owner = request.args.get('datasetOwner', default=None)
    dataset_description = request.args.get('datasetDescription', default=None)
    schema_name = request.args.get('schemaName', default=None)
    data = {
        'approved': 'true'
    }

    response = requests.put(
       f"{url}/api/v1/tickets/{ticket_id}",
       auth=HTTPBasicAuth(username, password)
       ,data=data
    )

    if response.status_code == 200:
        data = {
            'DATASET_NAME': dataset_name
            ,'TICKET_ID': ticket_id
            ,'DATASET_OWNER': dataset_owner
            ,'DATASET_DESCRIPTION': dataset_description
            ,'SCHEMA_NAME': schema_name
        }

        params = {'token':'deploy'}

        headers = {
            'Content-Type': 'application/json' 
        }
        response = requests.post(
            f"{jenkins_wrapper_url}/run-jenkins"
            ,data = json.dumps(data)
            ,params = params
            ,headers = headers
        )
        return "ticket has been successfully approved"
    
@app.route('/reject-ticket', methods=['PUT'])
def reject_ticket():
    ticket_id = request.args.get('ticketId', default=None)
    data = {
        'state': 'closed'
    }

    response = requests.put(
       f"{url}/api/v1/tickets/{ticket_id}",
       auth=HTTPBasicAuth(username, password),
       data=data
    )

    if response.status_code == 200:
        return "Ticket has been successfully rejected"
    else:
        return "Ticket couldn't be rejected"

@app.route('/listticket', methods=['GET'])
def ListTicket():
    logging.info('ListTicket function processed a request.')
    response = requests.get(
       f"{url}/api/v1/tickets/search?query=new approved:false",
       auth=HTTPBasicAuth(username, password)
    )

    if response.status_code == 200:
       result = response.json()
       users = result.get('assets').get('User')
       tickets = result.get('assets').get('Ticket')
       for ticket_id, ticket_info in tickets.items():
            response = requests.get(
                       f"{url}/api/v1/ticket_articles/by_ticket/{ticket_id}",
                       auth=HTTPBasicAuth(username, password)
                    )
            if response.status_code == 200:
                response_json = response.json()
                table_description = response_json[0]['body']

            customer_id = str(ticket_info['customer_id'])  # Ensure the key is a string for lookup
            user_info = users.get(customer_id, {})  # Get user details or an empty dict if not found
            # Adding user details to the ticket information
            ticket_info['customer_firstname'] = user_info.get('firstname', 'Unknown')
            ticket_info['customer_lastname'] = user_info.get('lastname', 'Unknown')
            ticket_info['customer_email'] = user_info.get('email', 'Unknown')
            ticket_info['table_description'] = table_description
       return tickets


@app.route('/showdatacatalog', methods=['GET'])
def ShowDataCatalog():
    ticket_id = request.args.get('ticketId', default=None)
    print(f"Ticket ID: {ticket_id}")
    article_response = requests.get(
       f"{url}/api/v1/ticket_articles/by_ticket/{ticket_id}",
       auth=HTTPBasicAuth(username, password)
    )
    
    articles = article_response.json()
    print(f"Articles: {articles}")
    filtered_articles = [item for item in articles if 'attachments' in item and item['attachments']]
    article_id = filtered_articles[0].get('id')
    attachments = filtered_articles[0].get('attachments')
    filtered_attachments = [item for item in attachments if 'filename' in item and item['filename'].endswith('.csv')]
    attachment_id = filtered_attachments[0].get('id')

    attachment_response = requests.get(
       f"{url}/api/v1/ticket_attachment/{ticket_id}/{article_id}/{attachment_id}",
       auth=HTTPBasicAuth(username, password)
    )

    attachment_output = attachment_response.text

    return attachment_output


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6080)

    
