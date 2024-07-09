from flask import Flask, request, jsonify
from flask_cors import CORS
from services import chat_start, get_user_info, chatbot_response

app = Flask(__name__)


# スレッドIDを受け取り、新しいセッションを作成する {"thread_id": "任意"}
@app.route("/start", methods=["POST"])
def start():
    thread_id = request.json.get("thread_id")
    chat_start(thread_id)
    user_info = get_user_info(thread_id)
    return jsonify(user_info)


@app.route("/export_userinfo", methods=["POST"])
def export_userinfo():
    thread_id = request.json.get("thread_id")
    user_info = get_user_info(thread_id)
    return jsonify(user_info)


@app.route("/chatting", methods=["POST"])
def chat():
    data = request.json
    thread_id = data.get("thread_id")
    user_message = data.get("message")
    return chatbot_response(thread_id, user_message)


if __name__ == "__main__":
    app.run(debug=True)
    # http://localhost:5000
