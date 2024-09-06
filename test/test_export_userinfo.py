import requests
import pprint
import json

# Flaskアプリケーションが動いているURL
url = "http://localhost:8000/export_userinfo"

# 送信するデータ
data = {"thread_id": "あああ"}

# POSTリクエストを送信
response = requests.post(url, json=data)

# レスポンスを表示
res_json = json.loads(response.text)
pprint.pprint(res_json)
