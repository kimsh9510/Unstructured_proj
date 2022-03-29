import requests

url = 'http://apis.data.go.kr/1741000/DisasterMsg3/getDisasterMsg1List'
params ={'serviceKey' : 'jPI0C9d3WB4hVbjtWVye1mYvAxDjIoC/Zu2HswIlVYUwxm8L2M0gZAyzMXCvLEWmaT8oI9r5WjLJaWhX3Eubag==', 'pageNo' : '1', 'numOfRows' : '100', 'type' : 'xml' }

response = requests.get(url, params=params)
print(response.content.decode('utf-8'))
