from schemas import User_info, User_infoEncoder
import json


def save_user_info_to_json(user_info, file_path):
    user_info_json = json.dumps(user_info, cls=User_infoEncoder, indent=4)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(user_info_json)


def decode_json_to_user_info(thread_id: str):
    file_path = "data/" + str(thread_id) + ".json"
    with open(file_path, "r") as f:
        data = json.load(f)
    user_info = User_info(data["thread_id"])
    # Hotellistデータの復元
    user_info.hotellist = data["hotellist"]
    # ConversationHistoryデータの復元
    user_info.conversation_history = data["conversation_history"]
    return user_info  # Class User_infoを返す
