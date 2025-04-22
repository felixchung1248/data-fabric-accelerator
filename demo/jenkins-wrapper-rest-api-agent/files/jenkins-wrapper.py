from flask import Flask,request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import logging
import os

app = Flask(__name__)
jenkins_url = os.environ['JENKINS_URL']

@app.route('/run-jenkins', methods=['POST'])
def callJenkins():
    logging.info("Jenkins wrapper received a request")
    job_name = request.args.get('token')  # Get job_name from URL query parameter
    if not job_name:
        return jsonify({'error': 'Missing token parameter'}), 400
    
    logging.info(f"Job name: {job_name}")
    post_params = request.get_json()

    logging.info(f"Params: {post_params}")

    # The base URL of the API you want to call
    target_base_url = jenkins_url

    # Construct the full URL with the job_name and other query parameters
    # The job_name is appended to the URL path
    target_url = f"{target_base_url}/generic-webhook-trigger/invoke"

    # Convert the post_params JSON body to a query string to append to target_url
    # If post_params is None or not a dictionary, default to an empty dict
    query_params = post_params if isinstance(post_params, dict) else {}
    query_params['token'] = job_name
    response = requests.post(target_url, params=query_params)    

    return response.text, response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)