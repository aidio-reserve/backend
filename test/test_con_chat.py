from sys import displayhook
import requests
import json
import pprint

# Flaskアプリケーションが動いているURL
url = "http://localhost:8000/chatting"

# 送信するデータ
data = {
    "thread_id": "20021114",
    "message": "草津温泉良いですね！",
}

# POSTリクエストを送信
response = requests.post(url, json=data)

# レスポンスを表示
# print(response.text)
res_json = json.loads(response.text)
pprint.pprint(res_json)
