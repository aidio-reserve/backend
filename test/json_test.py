import json


thread_id = "test"


class User_info:
    def __init__(self, thread_id):
        self.thread_id = thread_id
        self.hotellist = self.Hotellist()
        self.conversation_history = self.ConversationHistory()

    class Hotellist:
        def __init__(self):
            self.latitude = None
            self.longitude = None
            self.checkinDate = None
            self.checkoutDate = None
            self.detailClassCode = None
            self.adultNum = None
            self.upClassNum = None
            self.lowClassNum = None
            self.infantWithMBNum = None
            self.infantWithMNum = None
            self.infantWithBNum = None
            self.infantWithNoneNum = None
            self.roomNum = None
            self.maxCharge = None
            self.minCharge = None

    class ConversationHistory:
        def __init__(self):
            self.messages = []

        def add_message(self, speaker, message):
            self.messages.append((speaker, message))

    def to_dict(self):
        return {
            "thread_id": self.thread_id,
            "hotellist": vars(self.hotellist),
            "conversation_history": {"messages": self.conversation_history.messages},
        }


def json_make(user_info):
    data = user_info.to_dict()
    file_name = f"{data['thread_id']}.json"
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)


# 使用例
thread_id = "example_thread_id"
userinfo = User_info(thread_id)
json_make(userinfo)
