import requests

# Flaskアプリケーションが動いているURL
url = "http://localhost:5001/chatting"

# 送信するデータ
data = {"thread_id": "11111", "message": "こんにちは!"}

# POSTリクエストを送信
response = requests.post(url, json=data)

# レスポンスを表示
print(response.text)
