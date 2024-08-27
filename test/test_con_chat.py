import requests
import json

# Flaskアプリケーションが動いているURL
url = "http://localhost:8000/chatting"

# 送信するデータ
data = {
    "thread_id": "20021114",
    "message": "箱根で明後日から二泊三日、予算20000円で大人二名",
}

# POSTリクエストを送信
response = requests.post(url, json=data)

# レスポンスを表示
print(type(response))
print(response)
print(type(response.text))
print(response.text)
res_json = json.loads(response.text)
print(res_json["response"])
