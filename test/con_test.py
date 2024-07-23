import requests

# Flaskアプリケーションが動いているURL
url = "http://localhost:5001/chatting"

# 送信するデータ
data = {"thread_id": "12233445", "message": "箱根旅行に行きたいな"}

# POSTリクエストを送信
response = requests.post(url, json=data)

# レスポンスを表示
print(type(response.text))
print(response.text)
