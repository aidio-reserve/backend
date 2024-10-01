from google.cloud import firestore
from langchain_google_firestore import FirestoreChatMessageHistory

# 認証情報はデフォルトの認証情報を利用する
client = firestore.Client(project="aidio-reserve")

def saveAiMessage(thread_id, message):
    # FirestoreChatMessageHistoryの初期化
    chat_history = FirestoreChatMessageHistory(
        session_id = thread_id,
        collection = "threads",
        client = client
    )
    chat_history.add_ai_message(message)

def saveUserMessage(thread_id, message):
    # FirestoreChatMessageHistoryの初期化
    chat_history = FirestoreChatMessageHistory(
        session_id = thread_id,
        collection = "threads",
        client = client
    )
    chat_history.add_user_message(message)

def createThread(thread_id):
    doc_ref = client.collection("threads").document(thread_id)
    doc_ref.set({
        "chatting_start_time": firestore.SERVER_TIMESTAMP,
        "user_info":{"hotel_location": "",
            "checkinDate": "",
            "checkoutDate": "",
            "number_of_people": "",
            "minCharge": "",
            "maxCharge": ""},
    })

def loadChatHistory(thread_id):
    chat_history = FirestoreChatMessageHistory(
        session_id = thread_id,
        collection = "threads",
        client = client
    )
    return chat_history.messages

def renewUserInfoOnDB(thread_id, user_info):
    doc_ref = client.collection("threads").document(thread_id)
    doc_ref.update({
        "user_info": user_info
    })

def getUserInfoFromDB(thread_id):
    doc_ref = client.collection("threads").document(thread_id)
    return doc_ref.get().to_dict()["user_info"]



