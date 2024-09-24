from flask import Flask, request, jsonify
from schemas import UserInfo, HotelConditions
from services import process_message, process_display_hotel, get_hotelinfo_display
from models import (
    save_store,
    save_config,
    save_user_info,
    load_store,
    load_config,
    load_user_info,
)
from langchain_core.chat_history import InMemoryChatMessageHistory
import settings
import os

app = Flask(__name__)


@app.route("/start", methods=["POST"])
def initialize_user():
    """
    ユーザーの初期化を行うエンドポイント。

    クライアントから送信されたJSONデータから`thread_id`を取得し、
    新しいユーザーセッションを初期化します。具体的には以下の操作を行います:

    1. `thread_id`に基づいて新しい`InMemoryChatMessageHistory`オブジェクトを作成し、ストアに保存。
    2. `thread_id`を含む設定情報を作成し、保存。
    3. `thread_id`とデフォルトのホテル条件を持つ`UserInfo`オブジェクトを作成し、保存。
    4. 初期化されたユーザー情報をJSON形式で返却。

    Returns:
        Response: 初期化されたユーザー情報を含むJSONレスポンス。
    """
    thread_id = str(request.json.get("thread_id"))
    store = {}
    store[thread_id] = InMemoryChatMessageHistory()
    config = {"configurable": {"session_id": thread_id}}
    user_info = UserInfo(thread_id=thread_id, hotel_conditions=HotelConditions())
    # データを保存
    save_store(thread_id, store)
    save_config(thread_id, config)
    save_user_info(thread_id, user_info)

    return jsonify(user_info.get_thread_info())


@app.route("/export_userinfo", methods=["POST"])
def export_userinfo():
    """
    ユーザー情報をエクスポートするエンドポイント。

    クライアントから送信されたJSONデータから`thread_id`を取得し、
    該当するユーザー情報をロードして返却します。具体的には以下の操作を行います:

    1. `thread_id`に基づいてユーザー情報をロード。
    2. ユーザー情報が存在しない場合、404エラーを返却。
    3. ユーザー情報が存在する場合、その情報をJSON形式で返却。

    Returns:
        Response: ユーザー情報を含むJSONレスポンス、またはエラーメッセージ。
    """
    thread_id = str(request.json.get("thread_id"))
    # データをロード
    user_info = load_user_info(thread_id)

    if not user_info:
        return jsonify({"error": "User info not found"}), 404

    return jsonify(user_info.get_thread_info())


@app.route("/chatting", methods=["POST"])
def chat():
    """
    チャットメッセージを処理するエンドポイント。

    クライアントから送信されたJSONデータから`thread_id`と`message`を取得し、
    該当するセッションデータをロードしてAI応答を生成します。具体的には以下の操作を行います:

    1. `thread_id`に基づいてストア、設定、ユーザー情報をロード。
    2. 必要なデータが存在しない場合、404エラーを返却。
    3. ユーザーのメッセージを処理し、AI応答を生成。
    4. ユーザー情報を更新し、保存。
    5. AI応答を含むJSONレスポンスを返却。

    Returns:
        Response: AI応答を含むJSONレスポンス。
    """
    data = request.json
    thread_id = str(data.get("thread_id"))
    user_message = data.get("message")

    # データをロード
    store = load_store(thread_id)
    config = load_config(thread_id)
    user_info = load_user_info(thread_id)

    if not store or not config or not user_info:
        return jsonify({"error": "Session not found, please initialize first"}), 404

    ai_response = process_message(thread_id, user_message)
    display_hotel_bool = process_display_hotel(thread_id)
    user_info = load_user_info(thread_id)

    res = {
        "response": ai_response,
        "display_hotel": display_hotel_bool,
        "hotel_option": user_info.get_hotel_options(),
    }

    if display_hotel_bool == 1:
        hotel_info_display = get_hotelinfo_display(thread_id)
        res["hotel_info_display"] = hotel_info_display

    return jsonify(res)


if __name__ == "__main__":
    app.run(debug=True)
