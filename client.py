import requests
import base64

class APIClient:
    def __init__(self, base_url, access_token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        self.store = []

    def add_data(self, buffer, lat, lng):
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        self.store.append({
            'image': (f"data:image/jpeg;base64,{image_base64}"),
            'position': {
                'lat': lat,
                'lng': lng
            },
            'sizes': [
                {
                    'size': "small",
                    'width': 2,
                    'height': 1,
                    'length': 3
                },
            ],
            'material': "ASPHALT"
        })
    
    def get_data(self):
        return self.store

    def get_self(self):
        response = requests.get(self.base_url + "/machines/self", headers=self.headers)
        return self._handle_response(response, "GET")

    def create_explore(self):
        data = {
            "holds": self.store
        }
        response = requests.post(self.base_url + "/explores", headers=self.headers, json=data)
        return self._handle_response(response, "POST")

    def _handle_response(self, response, method):
        if response.status_code in [200, 201]:
            return response.json()
        else:
            return None

# if __name__ == "__main__":
#     api_client = APIClient(base_url='http://192.168.1.45:3000', access_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NmI4ZTUwODUwN2JjMjg3MmUxNTQ4N2EiLCJpYXQiOjE3MjMzOTMyODh9.dXdMnz1az1W88GOZYFNwzKcoQMezb4EUui1yxw4EZHE')
#     data = api_client.create_explore()
#     print(data)