import requests

# Flaskアプリケーションが動いているURL
url = "http://localhost:5000/export_userinfo"

# 送信するデータ
data = {"thread_id": "114514"}

# POSTリクエストを送信
response = requests.post(url, json=data)

# レスポンスを表示
print(response.text)
