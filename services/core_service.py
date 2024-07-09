from schemas import User_info
from models import save_user_info_to_json, decode_json_to_user_info
from services import add_message_to_conversation
from langchain import make_chatbot_response
import json


def chat_start(thread_id: str):
    user_info = User_info(thread_id)
    file_path = "data/" + str(thread_id) + ".json"
    save_user_info_to_json(user_info, file_path)


def get_user_info(thread_id: str):
    file_path = "data/" + str(thread_id) + ".json"
    with open(file_path, "r") as f:
        user_info = json.load(f)
    return user_info


def chatbot_response(thread_id: str, user_message: str):
    user_info = get_user_info(thread_id)  # ユーザー情報を取得 辞書型
    res = {}
    class_user_info = decode_json_to_user_info(thread_id)  # ユーザー情報を取得 クラス型
    class_user_info = add_message_to_conversation(
        class_user_info, user_message, True
    )  # ユーザーのメッセージを追加
    res["response"] = make_chatbot_response(user_info)

    user_info["user_message"] = user_message
    user_info["chatbot_response"] = "Hello, World!"
    file_path = "data/" + str(thread_id) + ".json"
    save_user_info_to_json(user_info, file_path)
    return user_info
