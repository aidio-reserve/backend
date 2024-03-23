from flask import Flask, request, jsonify, Blueprint
from .bot import core

app = Flask(__name__)

user_sessions = {}


def on_chat_start(thread_id):
    userinfo = core.User_info(thread_id)
    user_sessions[thread_id] = userinfo
    return jsonify(userinfo.to_dict())


def chatbot_response(thread_id, user_message):
    userinfo = user_sessions.get(thread_id)
    if not userinfo:
        return jsonify({"error": "Session not found"}), 404

    # ここでユーザーのメッセージを処理し、userinfoを更新
    c = core.make_message(user_message, userinfo)
    response_message = c[0]
    userinfo = c[1]

    user_sessions[thread_id] = userinfo

    return jsonify({"response": response_message, "userinfo": userinfo.to_dict()})


# Flaskのルート設定
@app.route("/")
def index():
    return "index page"


@app.route("/start", methods=["POST"])
def start():
    thread_id = request.json.get("thread_id")
    return on_chat_start(thread_id)


@app.route("/chatting", methods=["POST"])
def chat():
    data = request.json
    thread_id = data.get("thread_id")
    user_message = data.get("message")
    return chatbot_response(thread_id, user_message)


@app.route("/export_userinfo", methods=["POST"])
def export_userinfo():
    thread_id = request.json.get("thread_id")
    userinfo = user_sessions.get(thread_id)
    if not userinfo:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(userinfo.to_dict())
