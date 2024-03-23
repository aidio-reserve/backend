import requests

# Flaskアプリケーションが動いているURL
url = "http://localhost:5001/export_userinfo"

# 送信するデータ
data = {"thread_id": "12233445"}

# POSTリクエストを送信
response = requests.post(url, json=data)

# レスポンスを表示
print(response.text)
