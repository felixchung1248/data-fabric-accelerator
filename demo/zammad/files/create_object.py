# post_request.py
import requests
from requests.auth import HTTPBasicAuth
import os
import time

def test_connectivity(url, username, password, max_attempts=50, delay=10):
    """
    Test connectivity to a given URL, retrying until a connection is successful or max_attempts is reached.

    :param url: The URL to connect to.
    :param max_attempts: Maximum number of connection attempts.
    :param delay: Delay between attempts in seconds.
    """
    attempt = 0
    while attempt < max_attempts:
        try:
            response = requests.get(url, auth=(username, password))
            if response.status_code == 200:
                print(f"Successfully connected to {url}")
                return True
            else:
                print(f"Connected but received status code: {response.status_code}")
        except requests.ConnectionError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
        
        time.sleep(delay)
        attempt += 1
    
    print(f"Failed to connect after {max_attempts} attempts.")
    return False

def post_data(url, username, password, data=None):
    """
    Post data to a URL using basic authentication. The data field is optional.

    :param url: String, the URL to which the data is posted.
    :param username: String, the username for basic auth.
    :param password: String, the password for basic auth.
    :param data: Dictionary or None, the JSON data to post (optional).
    :return: requests.Response object.
    """
    headers = {'Content-Type': 'application/json'}
    if data is not None:
        response = requests.post(url, json=data, auth=HTTPBasicAuth(username, password), headers=headers)
    else:
        response = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers)
    return response

# Example usage
if __name__ == '__main__':
    host = os.environ["ZAMMAD_HOST"]
    token = os.environ["TOKEN"]
    # Define the URL
    url = f"{host}/api/v1/object_manager_attributes"

    # Define the data to be sent
    data1 = {
        "name": "approved",
        "object": "Ticket",
        "display": "Approved?",
        "active": "true",
        "position": 1550,
        "data_type": "boolean",
        "data_option": {
           "options": {
              "true": "yes",
              "false": "no"
           },
           "default": "false"
        },
        "screens": {
           "create_middle": {
              "ticket.customer": {
                 "shown": "true",
                 "required": "false",
                 "item_class": "column"
              },
              "ticket.agent": {
                 "shown": "true",
                 "required": "false",
                 "item_class": "column"
              }
           },
           "edit": {
              "ticket.customer": {
                 "shown": "true",
                 "required": "false"
              },
              "ticket.agent": {
                 "shown": "true",
                 "required": "false"
              }
           }
        }
    }

    data2 = {
        "name": "datasetname",
        "object": "Ticket",
        "display": "Dataset Name",
        "active": "true",
        "position": 901,
        "data_type": "input",
        "data_option": {
           "type": "text",
           "maxlength": 120
        },
        "screens": {
           "create_middle": {
              "ticket.customer": {
                 "shown": "true",
                 "required": "false",
                 "item_class": "column"
              },
              "ticket.agent": {
                 "shown": "true",
                 "required": "false",
                 "item_class": "column"
              }
           },
           "edit": {
              "ticket.customer": {
                 "shown": "true",
                 "required": "false"
              },
              "ticket.agent": {
                 "shown": "true",
                 "required": "false"
              }
           }
        }
    }

    # Basic auth credentials
    username = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]

    test_connectivity(f"{host}/api/v1/users",username,password)

    # Send the POST request
    response1 = post_data(url, username, password, data1)
    response2 = post_data(url, username, password, data2)
    response3 = post_data(f"{host}/api/v1/object_manager_attributes_execute_migrations", username, password)

    response4 = requests.delete(f"{host}/api/v1/tickets/1", auth=HTTPBasicAuth(username, password), headers={'Content-Type': 'application/json'})

    # Print the response
    print("Status Code:", response1.status_code)
    print("Response Body:", response1.text)
    print("Status Code:", response2.status_code)
    print("Response Body:", response2.text)
    print("Status Code:", response3.status_code)
    print("Response Body:", response3.text)