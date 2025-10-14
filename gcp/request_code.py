import requests

url = 'https://diabetes101-694276524349.europe-west1.run.app'

body = {
    "glucose": 210
}

response = requests.post(url, json=body)

print(response.text)