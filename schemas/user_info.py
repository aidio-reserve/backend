import datetime
import json


class User_info:
    def __init__(self, thread_id):
        self.thread_id = thread_id
        self.hotellist = self.Hotellist()
        self.conversation_history = self.ConversationHistory()

    class Hotellist:
        def __init__(self):
            self.latitude = 35.68183347805237
            self.longitude = 139.76802085456532
            self.checkinDate = str(datetime.date.today() + datetime.timedelta(days=1))
            self.checkoutDate = str(datetime.date.today() + datetime.timedelta(days=3))
            self.adultNum = 2
            self.upClassNum = 0
            self.lowClassNum = 0
            self.infantWithMBNum = 0
            self.infantWithMNum = 0
            self.infantWithBNum = 0
            self.infantWithNoneNum = 0
            self.roomNum = 1
            self.maxCharge = 50000
            self.minCharge = 1000

    class ConversationHistory:
        def __init__(self):
            self.messages = []

        def add_message(self, speaker, message):
            self.messages.append((speaker, message))


class User_infoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(
            obj, (User_info, User_info.Hotellist, User_info.ConversationHistory)
        ):
            return obj.__dict__
        return super().default(obj)
