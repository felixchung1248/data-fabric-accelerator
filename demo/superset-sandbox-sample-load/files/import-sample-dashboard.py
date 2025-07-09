import requests
import os
import time

# Superset API URL and Bearer Token
# superset_url = os.environ['SUPERSET_URL']
superset_url = "http://4.194.5.134:31888"
dashboard_path = os.environ['DASHBOARD_PATH']
superset_usr = os.environ['SUPERSET_USER']
superset_pw = os.environ['SUPERSET_PW']

class Importer:
    def __init__(self):
        self.session = requests.Session()
        self.wait_for_superset_service()
        self.get_superset_access_token()
        # self.get_csrf_token()
        
    def wait_for_superset_service(self, timeout=300, sleep_interval=5):
        """
        Waits for the Superset service to be up by repeatedly sending a health check request.
        
        Args:
            timeout (int): Maximum time to wait in seconds. Defaults to 300 seconds.
            sleep_interval (int): Time to wait between retries in seconds. Defaults to 5 seconds.
        """
        endpoint = "/health"
        url = f"{superset_url}{endpoint}"
        start_time = time.time()
        
        print("Waiting for Superset service to be up...")
        
        while True:
            try:
                response = self.session.get(url, timeout=5)
                print(response.text)
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
    
    def get_superset_access_token(self):
        # Authenticate and get access token
        endpoint = "/api/v1/security/login"
        url = f"{superset_url}{endpoint}"
        response = self.session.post(
            url,
            json={
                "username": superset_usr,
                "password": superset_pw,
                "provider": "db",
                "refresh": True
            },
        )
        if response.status_code != 200:
            raise Exception(f"Got HTTP code of {response.status_code} from {url}; expected 200")
        access_token = response.json()["access_token"]
        print(f"Received access token: {access_token}")
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}"
        })
        # print(f"Session ID from get_superset_access_token: {self.session.cookies.get('sessionid')}")
        
    def get_csrf_token(self):
        endpoint = "/api/v1/security/csrf_token/"  # Trailing slash required to avoid redirect"
        url = f"{superset_url}{endpoint}"
        response = self.session.get(url)
        if response.status_code != 200:
            raise Exception(f"Got HTTP code of {response.status_code} from {url}; expected 200")
        token = response.json()["result"]
        print(f"Received CSRF token: {token}")
        self.session.headers.update({
            "X-CSRFToken": token
            ,'Referer': superset_url
        })
        # print(f"Session ID from get_csrf_token: {self.session.cookies['sessionid']}")
        
    def import_dashboard(self, zip_file_path):
        endpoint = "/api/v1/dashboard/import/"
        url = f"{superset_url}{endpoint}"
        with open(zip_file_path, 'rb') as infile:
            files = {'formData': ('dashboard.zip', infile.read(), 'application/zip')}
        # payload={
        #     'passwords': '{"databases/'+database_name+'": "'+database_password+'"}',
        #     'overwrite': 'true'
        # }
        # print(f"Session ID from import_dashboard: {self.session.cookies['sessionid']}")
        
        response = self.session.post(
            url,
            files=files
            # data=payload
        )
        
        print(response.text)
        
        # Ensure we got the expected 200 status code
        if response.status_code != 200:
            raise Exception(
                f"Got HTTP code of {response.status_code} from {url}; expected 200.  See server logs for possible hints"
            )

        # Ensure we can parse the response as JSON
        try:
            response_json = response.json()
        except Exception as exception:
            raise Exception(f"Could not parse response from {url} as JSON (see server logs for possible hints)")

        # Ensure that the JSON has a 'message' field
        try:
            message = response_json["message"]
        except KeyError as exception:
            raise Exception(f"Could not find 'message' field in response from {url}, got {response_json}")

        # Ensure that the 'message' field contains 'OK'
        if message != "OK":
            raise Exception(f"Got message '{message}' from {url}; expected 'OK'")

        print("Dashboard imported successfully")

if __name__ == "__main__":
    
    importer = Importer()
    importer.import_dashboard(dashboard_path)