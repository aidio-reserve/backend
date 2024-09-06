from sys import displayhook
import requests
import json
import pprint

# Flaskアプリケーションが動いているURL
url = "http://localhost:8000/chatting"

# 送信するデータ
data = {
    "thread_id": "あああ",
    "message": "10月4日から二日間で考えています",
}

# POSTリクエストを送信
response = requests.post(url, json=data)

# レスポンスを表示

res_json = json.loads(response.text)
pprint.pprint(res_json)
