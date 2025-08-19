import requests
import os
import json

# Function to look up id by name
def get_id_by_name(name, data):
    for item in data:
        if item['name'] == name:
            return item['id']
    return None  # Return None if name is not found

# Superset API URL and Bearer Token
superset_url = os.environ['SUPERSET_URL']

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
