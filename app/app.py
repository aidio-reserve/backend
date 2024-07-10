from flask import Flask, request, jsonify
from flask_cors import CORS
from .bot import core
import json
from pathlib import Path

app = Flask(__name__)


def decode_json_to_userinfo(file_name):
    with open(file_name, "r") as file:
        data = json.load(file)

    user_info = core.User_info(data["thread_id"])

    # Hotellistデータの復元
    for key, value in data["hotellist"].items():
        setattr(user_info.hotellist, key, value)

    # ConversationHistoryデータの復元
    for message in data["conversation_history"]["messages"]:
        user_info.conversation_history.add_message(*message)

    return user_info


def json_make(user_info):
    data = user_info.to_dictionary()
    file_name = f"{data['thread_id']}.json"
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)


def chat_start(thread_id: str):
    user_info = core.User_info(thread_id)
    json_make(user_info)


def chatbot_response(thread_id, user_message):

    user_info = decode_json_to_userinfo(str(thread_id) + ".json")
    print(user_info)

    # ここでユーザーのメッセージを処理し、userinfoを更新
    c = core.make_message(user_message, user_info)
    response_message = c[0]
    user_info = c[1]
    print(user_info)

    # 更新したuserinfoをファイルに保存
    json_make(user_info)

    display_hotel = core.display_hotel(user_message)

    res = {}
    res["response"] = response_message
    res["display_hotel"] = display_hotel
    res["hotel_option"] = user_info.hotellist.to_dict()
    return jsonify(res)


def export_userinfo(thread_id):
    f = open(str(thread_id) + ".json", "r")
    user_info = json.load(f)
    f.close()
    print(user_info)
    return jsonify(user_info)


# Flaskのルート設定
@app.route("/")
def index():
    return "index page"


# スレッドIDを受け取り、新しいセッションを作成する {"thread_id": "任意"}
@app.route("/start", methods=["POST"])
def start():
    thread_id = request.json.get("thread_id")
    chat_start(thread_id)
    f = open(str(thread_id) + ".json", "r")
    user_info = json.load(f)
    f.close()
    return jsonify(user_info)


# ユーザーのメッセージを受け取り、応答を返す {"thread_id": "任意", "message": "任意"}
@app.route("/chatting", methods=["POST"])
def chat():
    data = request.json
    thread_id = data.get("thread_id")
    user_message = data.get("message")
    return chatbot_response(thread_id, user_message)


# スレッドIDを受け取り、ホテル情報を返す {"thread_id": "任意"}
@app.route("/export_userinfo", methods=["POST"])
def userinfo():
    thread_id = request.json.get("thread_id")
    return export_userinfo(thread_id)
