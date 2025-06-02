import requests
import time
import pynessie

nessie_url=os.environ['NESSIE_URL']
nessie_schema=os.environ['NESSIE_SCHEMA']

def check_nessie_catalog_health(url):
    """
    Check the healthiness of a Nessie catalog URL by verifying the response code.

    Args:
        url (str): The Nessie catalog URL to check.

    Returns:
        bool: True if the response code is 200, False otherwise.
    """
    try:
        # Send a GET request to the Nessie catalog URL
        response = requests.get(url, timeout=10)
        
        # Check if the response code is 200
        if response.status_code == 200:
            print(f"SUCCESS: The URL '{url}' is healthy (Response Code: 200).")
            return True
        else:
            print(f"WARNING: The URL '{url}' returned a non-200 status code: {response.status_code}.")
            return False
    except requests.exceptions.RequestException as e:
        # Handle any exceptions during the request
        print(f"ERROR: Failed to access the URL '{url}'. Exception: {e}")
        return False

def create_schema():
    """
    Action to perform when the Nessie catalog URL is healthy.
    Replace this function with your desired action.
    """
    print("Performing some action because the URL is healthy!")
    # Add your custom logic here
    # For example: Trigger a task, send a notification, etc.

if __name__ == "__main__":
    # Replace with the actual Nessie catalog URL you want to check
    nessie_catalog_url = nessie_url
    
    while True:
        # Check the health of the Nessie catalog URL
        if check_nessie_catalog_health(nessie_catalog_url):
            # If healthy, perform some action and optionally break the loop
            create_schema()
            break  # Exit the loop after the action is performed
        
        # If not healthy, wait before checking again
        print("Retrying in 10 seconds...")
        time.sleep(10)