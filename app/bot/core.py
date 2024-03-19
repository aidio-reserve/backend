import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import settings
import json
from . import placement
from . import export_address
from . import lang_chains as LC
from langchain.chat_models import ChatOpenAI
from typing import Optional

OPENAI_API_KEY = settings.OPENAI_API_KEY

chat = ChatOpenAI(model="gpt-3.5-turbo")


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


# 必須である情報:middleClassCode,smallClassCode,checkinDate,checkoutDate \n
# 必須でない情報:detailClassCode,adultNum,upClassNum,lowClassNum,infantWithMBNum,infantWithMNum,infantWithBNum,infantWithNoneNum,roomNum,maxCharge,minCharge\n

makelist_chain = LC.MakeList()
make_conversation_chain = LC.MakeConversation()


def make_message(user_message: str, userinfo: User_info):

    # ユーザーのメッセージに含まれる地名を取得
    user_landmark = export_address.ExportLandmarkChain().run(user_message)
    if user_landmark is None:
        landmarks = "無し"
    else:
        user_landmark += " " + str(
            export_address.ExportprefectureAddress().export_prefecture_address(
                user_landmark
            )
        )

    # ユーザーのメッセージを履歴に追加
    userinfo.conversation_history.add_message(
        "User", user_message + " location:" + str(user_landmark)
    )

    # 会話履歴よりホテルリストを更新
    new_hotel_list = makelist_chain.run(
        content=str(userinfo.conversation_history.messages),
        hotelinfo=str(userinfo.hotellist),
    )
    new_hotel_list = json.loads(new_hotel_list)
    userinfo.hotellist = new_hotel_list

    # AIコンシェルジュによる応答を生成
    concierge_response = make_conversation_chain.run(
        recent_message=user_message,
        conversation_history=str(userinfo.conversation_history),
        hotelinfo=str(userinfo.hotellist),
    )

    # AIコンシェルジュの応答に含まれる地名を取得
    concierge_landmark = export_address.ExportLandmarkChain().run(
        str(concierge_response)
    )
    if concierge_landmark is None:
        concierge_landmark = "無し"
    else:
        concierge_landmark += " " + str(
            export_address.ExportprefectureAddress().export_prefecture_address(
                concierge_landmark
            )
        )

    # AIコンシェルジュの応答を履歴に追加
    userinfo.conversation_history.add_message(
        "Concierge",
        concierge_response + "location:" + str(concierge_landmark),
    )

    # 会話履歴よりホテルリストを更新
    new_hotel_list = makelist_chain.run(
        content=str(userinfo.conversation_history.messages),
        hotelinfo=str(userinfo.hotellist),
    )
    new_hotel_list = json.loads(new_hotel_list)
    userinfo.hotellist = new_hotel_list

    # 会話履歴より、現在の話題に関連する地名を取得
    landmarks = placement.export_conversation_landmark(
        str(userinfo.conversation_history.messages)
    )

    print(landmarks)

    if landmarks is None:
        landmarks = "無し"
    else:
        landmarks += " " + str(
            export_address.ExportprefectureAddress().export_prefecture_address(
                landmarks
            )
        )
        # ランドマークの緯度経度を取得し、ホテルリストに追加
        place = placement.export_letitude_longitude(landmarks)
        userinfo.hotellist["latitude"] = place[0]
        userinfo.hotellist["longitude"] = place[1]

    return concierge_response, userinfo


#  "hotelinfo": str(hotel_list.__dict__)
