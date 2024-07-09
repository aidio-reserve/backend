from schemas import User_info
from models import save_user_info_to_json, decode_json_to_user_info
from services import get_user_info


def add_message_to_conversation(user_info: User_info, message: str, is_user: bool):
    if is_user:
        user_info.conversation_history.append({"user": message})
    else:
        user_info.conversation_history.append({"chatbot": message})
    return user_info
