from dotenv import load_dotenv
import requests
import os

load_dotenv()

apiToken = os.getenv('API_TOKEN')

data = {
	'memberid': "49073"
}
headers = {'Authorization': apiToken}

response = requests.delete(url="https://livebackend.texco.in/api/members", data=data, headers=headers)

try:
	print(response.json())
except:
	pass

try:
	print(response.text)
except:
	pass
