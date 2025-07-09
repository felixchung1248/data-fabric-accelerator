import requests
import os
import json
import time

# Function to look up id by name
def get_id_by_name(name, data):
    for item in data:
        if item['name'] == name:
            return item['id']
    return None  # Return None if name is not found

# Superset API URL and Bearer Token
superset_url = os.environ['SUPERSET_URL']

endpoint = "/health"
url = f"{superset_url}{endpoint}"
start_time = time.time()

print("Waiting for Superset service to be up...")
timeout=300
sleep_interval=5

while True:
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("Superset service is up!")
            break
    except requests.exceptions.RequestException:
        pass  # Ignore connection errors and keep retrying
    
    elapsed_time = time.time() - start_time
    if elapsed_time > timeout:
        raise Exception(f"Superset service did not become available within {timeout} seconds")
    
    print(f"Superset service not available yet, retrying in {sleep_interval} seconds...")
    time.sleep(sleep_interval)

# Headers for the API request
headers = {
    "Content-Type": "application/json"
}

# Payload to login
payload = {
   "username": os.environ['SUPERSET_USER'],
   "password": os.environ['SUPERSET_PW'],
   "provider": "db"
}

# Make the POST request
response = requests.post(superset_url+"/api/v1/security/login", headers=headers, json=payload)     
bearer_token = response.json().get('access_token')

# Headers for the API request
headers = {
    "Authorization": f"Bearer {bearer_token}",
    "Content-Type": "application/json"
}

# Payload to create a role
userRoles_str = os.environ['USER_ROLES']
userRoles = json.loads(userRoles_str)

for userRole in userRoles:
    # Make the POST request
    response = requests.post(superset_url+"/api/v1/security/roles", headers=headers, json=userRole)
    
role_responses = requests.get(superset_url+"/api/v1/security/roles", headers=headers)
roles = role_responses.json().get('result')

# Payload to create an user
user_str = os.environ['USERS']
users = json.loads(user_str)

for user in users:
    roleNames = user.get('roles')
    roleIds = []
    for roleName in roleNames:
        roleIds.append(get_id_by_name(roleName,roles))
        user['roles'] = roleIds
        response = requests.post(superset_url+"/api/v1/security/users", headers=headers, json=user)
        print(response.text)