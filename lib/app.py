import sys

sys.path.append("../")
import settings
import export_address
import json
import pprint
import placement
import lang_chains as LC
import chainlit as cl
from langchain.chains import ConversationChain, LLMChain, SimpleSequentialChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import (
    ConversationBufferMemory,
    RedisChatMessageHistory,
    ConversationSummaryMemory,
)
from langchain.output_parsers import PydanticOutputParser
from typing import Optional
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain.schema import HumanMessage
from pydantic import BaseModel

OPENAI_API_KEY = settings.OPENAI_AK
REDIS_URL = settings.REDIS_URL

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


# 必須である情報:middleClassCode,smallClassCode,checkinDate,checkoutDate \n
# 必須でない情報:detailClassCode,adultNum,upClassNum,lowClassNum,infantWithMBNum,infantWithMNum,infantWithBNum,infantWithNoneNum,roomNum,maxCharge,minCharge\n


@cl.on_chat_start
async def on_chat_start():
    thread_id = None
    while not thread_id:  # ← スレッドIDが入力されるまで繰り返す
        res = await cl.AskUserMessage(
            content="私はあなたの旅行体験をサポートするコンシェルジュです。スレッドIDを入力してください。",
            timeout=600,
        ).send()  # ← AskUserMessageを使ってスレッドIDを入力
        if res:
            thread_id = res["content"]

    makelist_chain = LC.MakeList()
    make_conversation_chain = LC.MakeConversation()

    userinfo = User_info(thread_id)

    cl.user_session.set("makelist_chain", makelist_chain)
    cl.user_session.set("make_conversation_chain", make_conversation_chain)
    cl.user_session.set("userinfo", userinfo)
    cl.user_session.set("thread_id", thread_id)


@cl.on_message
async def on_message(message: str):
    makelist_chain = cl.user_session.get("makelist_chain")
    make_conversation_chain = cl.user_session.get("make_conversation_chain")
    userinfo = cl.user_session.get("userinfo")
    thread_id = cl.user_session.get("thread_id")

    user_landmark = export_address.ExportLandmarkChain().run(message)
    if user_landmark is None:
        landmarks = "無し"
    else:
        user_landmark += " " + str(
            export_address.ExportprefectureAddress().export_prefecture_address(
                user_landmark
            )
        )

    userinfo.conversation_history.add_message(
        "User", message + " location:" + str(user_landmark)
    )

    new_hotel_list = makelist_chain.run(
        content=str(userinfo.conversation_history.messages),
        hotelinfo=str(userinfo.hotellist),
    )

    new_hotel_list = json.loads(new_hotel_list)
    userinfo.hotellist = new_hotel_list

    print(userinfo.hotellist)

    print(user_landmark)

    concierge_response = make_conversation_chain.run(
        recent_message=message,
        conversation_history=str(userinfo.conversation_history),
        hotelinfo=str(userinfo.hotellist),
    )

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

    userinfo.conversation_history.add_message(
        "Concierge",
        concierge_response + "location:" + str(concierge_landmark),
    )

    new_hotel_list = makelist_chain.run(
        content=str(userinfo.conversation_history.messages),
        hotelinfo=str(userinfo.hotellist),
    )

    new_hotel_list = json.loads(new_hotel_list)
    userinfo.hotellist = new_hotel_list

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
        place = placement.export_letitude_longitude(landmarks)
        userinfo.hotellist["latitude"] = place[0]
        userinfo.hotellist["longitude"] = place[1]

    res = str((userinfo.conversation_history.messages)) + "\n" + str(userinfo.hotellist)

    cl.user_session.set("userinfo", userinfo)

    await cl.Message(res).send()


#  "hotelinfo": str(hotel_list.__dict__)
