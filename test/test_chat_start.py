import requests

# Flaskアプリケーションが動いているURL
url = "http://localhost:8000/start"

# 送信するデータ
data = {"thread_id": "20021114"}

# POSTリクエストを送信
response = requests.post(url, json=data)

# レスポンスを表示
print(response.text)
