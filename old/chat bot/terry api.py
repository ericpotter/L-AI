import requests

url = 'http://ncuterryobe.pythonanywhere.com/api'

# POST 請求的資料
data = {
    'key': 'Eric',
    's': '我腸胃不適，平常流很多汗，常常想咳嗽'
}

# 發送 POST 請求
response_post = requests.post(url, json=data)
print('POST 請求:')
print('狀態碼:', response_post.status_code)
print('響應內容:', response_post.json())