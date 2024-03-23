import requests

# Flaskアプリケーションが動いているURL
url = "http://localhost:5001/start"

# 送信するデータ
data = {"thread_id": "11111"}

# POSTリクエストを送信
response = requests.post(url, json=data)

# レスポンスを表示
print(response.text)
