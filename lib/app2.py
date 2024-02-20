import sys

sys.path.append("../")
import settings
import export_address
import json
import pprint
import placement
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


class MakeList:
    makelist_prompt = PromptTemplate(
        input_variables=["content", "hotelinfo"],
        template="""
        あなたへの指示:
        あなたは、JSON形式の情報を出力するように設計されている。
        UserとConciergeの会話と、ホテルの条件リストJSON各種パラメータの説明と、現在のホテルの条件リストが与えられる。会話の流れを元に、ホテルの条件リストの一部を更新、変更したJSONを、ホテルの条件リストJSON各種パラメータの説明と以下の要件に従って出力しなさい。
        UserとConciergeの発言は「('User','XXX location:foo')」「('Concierge','YYY location:bar')」のリストで与えられる。UserとConciergeの発言には   「location」に会話の中に含まれる地名、観光地名、場所名、ランドマーク、伝統工芸品、シンボルなどが含まれている。
        UserとConciergeの会話及びホテルの条件リストから読み取った、各種日付、人数、金額、部屋数などの情報をパラメータに代入し、未確定の情報のパラメータにはNoneを代入しなさい。
        ## 注意
        - 会話及びホテルの条件リストから読み取った、確定している情報のみをパラメータに代入し、未確定の情報のパラメータにはNoneを代入しなさい。
        \n
        ユーザーの会話:
        {content}
        \n
        ホテルの条件リストJSON各種パラメータの説明:
        latitude: 変更しない
        longitude: 変更しない
        checkinDate: (チェックインする日付(YYYY-MM-DD)、(例:2024-10-01, None))
        checkoutDate: (チェックアウトする日付(YYYY-MM-DD)、(例:2024-10-02, None))
        detailClassCode: (駅や詳細地域などの細かい区分、(例:biwako, tokyoeki, rakutenchi, None))
        adultNum: (大人の人数、(例:2))
        upClassNum: (小学生高学年の人数、(例:1))
        lowClassNum: (小学生低学年の人数、(例:0))
        infantWithMBNum: (幼児(食事・布団付)の人数、(例:1))
        infantWithMNum: (幼児(食事のみ)の人数、(例:1))
        infantWithBNum: (幼児(布団のみ)の人数、(例:1))
        infantWithNoneNum: (幼児(食事・布団不要)の人数、(例:1))
        roomNum: (部屋数、(例:1, None))
        maxCharge: (上限金額、(例:60000, None))
        minCharge: (下限金額、(例:50000, None))
        \n
        現在のホテルの条件リスト:
        {hotelinfo}
        \n
        JSON
        """,
    )

    makelist_chat = ChatOpenAI(model="gpt-3.5-turbo")

    def __init__(self):
        self.makelist_chain = LLMChain(
            llm=self.makelist_chat, prompt=self.makelist_prompt
        )

    def run(self, content, hotelinfo):
        return self.makelist_chain.run(content=content, hotelinfo=hotelinfo)


class MakeConversation:

    makeconversation_prompt = PromptTemplate(
        input_variables=["recent_message", "conversation_history", "hotelinfo"],
        template="""
        あなたへの指示:
        あなたはUserの旅行体験をサポートするConciergeである。これまでのUserとConciergeの会話の流れ、最新のUserの発言、現在Userが泊まろうとしているホテルの条件が与えられる。会話の流れをもとに、どのような旅行体験を提案するか、どのような場所へ行くのか、いつからいつまで旅行に行くのかをUserから聞き出しなさい。適宜、旅行体験をサポートするような情報提供を行いなさい。最新のUserの発言に対して、適切な返答を出力しなさい。100字以内で出力しなさい。
        ## 注意
        - 会話の流れは、UserとConciergeの会話の流れをリストで与えられる
        - 会話の流れは、UserとConciergeの発言が交互に与えられる
        - 会話の流れは、UserとConciergeの発言は「('User','XXX location:foo')」「('Concierge','YYY location:bar')」のリストで与えられる
        - 会話の流れは、UserとConciergeの発言には「location」に「都道府県,市町村」が含まれている
        - 会話の流れは、UserとConciergeの発言は最新のものが最後に来るように与えられる
        - Userの発言にlocation情報が含まれない場合、会話に沿った日本国内の観光地を提案しなさい。
        \n
        最新のUserの発言: {recent_message}
        \n
        これまでの会話の流れ: {conversation_history}
        \n
        現在のホテルの条件リスト: {hotelinfo}
        """,
    )

    make_conversation_chat = ChatOpenAI(model="gpt-3.5-turbo")

    def __init__(self):
        self.make_conversation_chain = LLMChain(
            llm=self.make_conversation_chat, prompt=self.makeconversation_prompt
        )

    def run(self, recent_message, conversation_history, hotelinfo):
        return self.make_conversation_chain.run(
            recent_message=recent_message,
            conversation_history=conversation_history,
            hotelinfo=hotelinfo,
        )


class MakePlace:
    makeplace_prompt = PromptTemplate(
        input_variables=["content"],
        template="""
        あなたへの指示:
        UserとConciergeの会話が与えられる。会話の内容を元に、現在Userがどこへ行きたいのか、地名、観光地名、場所名、ランドマーク、伝統工芸品、シンボルなどを抽出し、それを出力しなさい。
        ## 注意
        - 会話の内容は、UserとConciergeの会話が与えられる
        - 会話の内容は、UserとConciergeの発言が交互に与えられる
        - 会話の内容は、UserとConciergeの発言は「('User','XXX location:foo')」「('Concierge','YYY location:bar')」のリストで与えられる
        \n
        {content}
        \n
        location:
        """,
    )

    makeplace_chat = ChatOpenAI(model="gpt-3.5-turbo")

    def __init__(self):
        self.makeplace_chain = LLMChain(
            llm=self.makeplace_chat, prompt=self.makeplace_prompt
        )

    def run(self, content):
        landmark = self.makeplace_chain.run(content=content)
        return landmark


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

    makelist_chain = MakeList()
    make_conversation_chain = MakeConversation()

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
