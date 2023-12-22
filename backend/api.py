import requests

class APIWrapper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None  # Store the session token

    def make_another_request(self, route, data=None):
        url = f"{self.base_url}/{route}"

        # Check if the session token is available or renew
        if not self.token:
            login_data = {
                "username": "admin",
                "password": "password"
            }
            login_url = f"{self.base_url}/Authentication/Authenticate"
            response = self.session.post(login_url, json=login_data, verify=False)

            if response.status_code == 200:
                response_json = response.json()
                if 'sessionToken' in response_json:
                    self.token = response_json['sessionToken']
            else:
                return None  # Return None for a failed login

        # Include the token in the request headers
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.session.get(url, json=data, headers=headers, verify=False)

        if response.status_code == 200:
            return response.json()  # Return the JSON response for a successful request
        else:
            return None  # Return None for a failed request

# API URL
api_url = "http://librebooking.teste/Web/Services"

# Creating an instance of the APIWrapper class
api_wrapper = APIWrapper(api_url)

# Making another request to a different route
route_destination = "Schedules"
request_data = {
    "schedules": 
        [ { 
                "daysVisible": 5,
                "id": 123, "isDefault": "true", 
                "name": "schedule name", 
                "timezone": "timezone_name", 
                "weekdayStart": 0, 
                "availabilityBegin": "2023-01-18T21:09:54-0500", 
                "availabilityEnd": "2023-02-07T21:09:54-0500", 
                "maxResourcesPerReservation": 10, 
                "totalConcurrentReservationsAllowed": 0, 
                "links": [], 
                "message": "null" 
        } 
        ], 
    "links": [], "message": "null"
}

response_data = api_wrapper.make_another_request(route_destination, request_data)

# Process response_data as needed
print(response_data)
