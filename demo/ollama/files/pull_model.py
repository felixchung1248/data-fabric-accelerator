# post_request.py
import requests
from requests.auth import HTTPBasicAuth
import os
import time

def test_connectivity(url, max_attempts=50, delay=10):
    """
    Test connectivity to a given URL, retrying until a connection is successful or max_attempts is reached.

    :param url: The URL to connect to.
    :param max_attempts: Maximum number of connection attempts.
    :param delay: Delay between attempts in seconds.
    """
    attempt = 0
    while attempt < max_attempts:
        try:
            response = requests.get(url)
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

def post_data(url,model):
    data = {"model": model}
    response = requests.post(url, json=data)
    return response

# Example usage
if __name__ == '__main__':
    host = os.environ["OLLAMA_HOST"]
    model = os.environ["OLLAMA_MODEL"]
    # Define the URL
    url = f"{host}/api"

    test_connectivity(f"{url}/version")

    # Send the POST request
    response1 = post_data(f"{url}/pull",model)

    # Print the response
    print("Status Code:", response1.status_code)
    print("Response Body:", response1.text)