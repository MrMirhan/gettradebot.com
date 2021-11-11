import requests

r = requests.get("http://185.114.21.56", json={"xd": "test"})
print(r)