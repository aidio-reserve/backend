import sys

sys.path.append("../")
import settings
import export_address
import json
import placement
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate, FewShotPromptTemplate

from geopy.geocoders import Nominatim

OPENAI_API_KEY = settings.OPENAI_AK

chat = ChatOpenAI(model="gpt-3.5-turbo")


# 会話履歴からUserの求めるホテルの条件JSONを出力する
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


# 会話履歴からUserの求める旅行体験を提案するConciergeの返答を出力する
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


# 発言からランドマークを抽出する
class ExportLandmarkChain:

    chat = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

    def __init__(self):
        llm = self.chat
        example_landmark_conversion = [
            {
                "input": "加賀温泉いいですね",
                "output": "加賀温泉",
            },
            {
                "input": "富士山を見たい",
                "output": "富士山",
            },
            {
                "input": "北陸が良い",
                "output": None,
            },
            {
                "input": "中国地方に行きたい",
                "output": None,
            },
            {
                "input": "温泉旅行が気になります",
                "output": None,
            },
            {
                "input": "こんにちは",
                "output": None,
            },
            {
                "input": "None",
                "output": None,
            },
            {
                "input": "none",
                "output": None,
            },
            {
                "input": "null",
                "output": None,
            },
            {
                "input": "北海道に行きたい",
                "output": "北海道",
            },
            {
                "input": "南部鉄器を買いたい",
                "output": "南部鉄器",
            },
            {
                "input": "東京タワーに行きたい",
                "output": "東京タワー",
            },
            {
                "input": "USJいきてえ",
                "output": "USJ",
            },
            {
                "input": "おはようございます。旅行の計画はお決まりですか？日本国内での観光地を提案いたします。例えば、京都や沖縄など、どちらがお好みでしょうか？ご旅行の期間やご予算なども教えていただけますか？",
                "output": "京都・沖縄",
            },
            {
                "input": "沖縄は美しいビーチや美味しい食べ物がたくさんあります。また、沖縄の伝統工芸品やシンボルもたくさんあります。",
                "output": "沖縄",
            },
            {
                "input": "温泉旅行ですね！日本には多くの素晴らしい温泉地があります。例えば箱根や草津温泉などがおすすめです。",
                "output": "箱根・草津",
            },
        ]
        example_landmark_conversion_prompt = PromptTemplate(
            input_variables=["input", "output"],
            template="Userの発言: {input}\n location: {output}",
        )
        get_landmark_prompt = FewShotPromptTemplate(
            input_variables=["content"],
            examples=example_landmark_conversion,
            example_prompt=example_landmark_conversion_prompt,
            prefix="""
                    Userの発言が与えられる。Userの発言には、地名、観光地名、場所名、ランドマーク、伝統工芸品、シンボルなどが含まれている場合がある。
                    その地名、観光地名、場所名、ランドマーク、伝統工芸品、シンボルなどを抽出し、それを出力しなさい。
                    抽出できない場合は、Noneと出力しなさい。\n
                    \n
                """,
            suffix="Userの発言: {content}\n location:",
        )
        self.get_landmark_chain = LLMChain(
            llm=llm,
            prompt=get_landmark_prompt,
        )

    def run(self, content):
        return self.get_landmark_chain.run(content=content)


# 発言から都道府県名を抽出する
class ExportprefectureAddress:
    def __init__(self):
        self.chain1 = self.GetAddressChain()
        self.chain2 = self.GetAddressPrefectureChain()

    class GetAddressChain:

        chat = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)

        def __init__(self):
            llm = self.chat
            example_landmark_conversion = [
                {
                    "input": "加賀温泉いいですね",
                    "output": "加賀温泉",
                },
                {
                    "input": "富士山を見たい",
                    "output": "富士山",
                },
                {
                    "input": "北陸が良い",
                    "output": None,
                },
                {
                    "input": "中国地方に行きたい",
                    "output": None,
                },
                {
                    "input": "温泉旅行が気になります",
                    "output": None,
                },
                {
                    "input": "こんにちは",
                    "output": None,
                },
                {
                    "input": "None",
                    "output": None,
                },
                {
                    "input": "none",
                    "output": None,
                },
                {
                    "input": "null",
                    "output": None,
                },
                {
                    "input": "北海道に行きたい",
                    "output": "北海道",
                },
                {
                    "input": "南部鉄器を買いたい",
                    "output": "南部鉄器",
                },
                {
                    "input": "東京タワーに行きたい",
                    "output": "東京タワー",
                },
                {
                    "input": "USJいきてえ",
                    "output": "USJ",
                },
            ]
            example_landmark_conversion_prompt = PromptTemplate(
                input_variables=["input", "output"],
                template="Userの発言: {input}\n location: {output}",
            )
            get_landmark_prompt = FewShotPromptTemplate(
                input_variables=["content"],
                examples=example_landmark_conversion,
                example_prompt=example_landmark_conversion_prompt,
                prefix="""
                    Userの発言が与えられる。Userの発言には、地名、観光地名、場所名、ランドマーク、伝統工芸品、シンボルなどが含まれている場合がある。
                    その地名、観光地名、場所名、ランドマーク、伝統工芸品、シンボルなどを抽出し、それを出力しなさい。
                    抽出できない場合は、Noneと出力しなさい。\n
                    \n
                """,
                suffix="Userの発言: {content}\n location:",
            )
            self.get_landmark_chain = LLMChain(
                llm=llm,
                prompt=get_landmark_prompt,
            )

        def run(self, content):
            return self.get_landmark_chain.run(content=content)

    class GetAddressPrefectureChain:

        chat = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)

        def __init__(self):
            llm = self.chat
            example_get_location = [
                {
                    "input": "東京都庁",
                    "output": "tokyo",
                },
                {
                    "input": "加賀温泉",
                    "output": "ishikawa",
                },
                {
                    "input": "富士山",
                    "output": "shizuoka",
                },
                {
                    "input": "北海道",
                    "output": "hokkaido",
                },
                {
                    "input": "南紀白浜空港",
                    "output": "wakayama",
                },
                {
                    "input": "北陸",
                    "output": None,
                },
                {
                    "input": "中国地方",
                    "output": None,
                },
                {
                    "input": "None",
                    "output": None,
                },
                {
                    "input": "none",
                    "output": None,
                },
                {
                    "input": "null",
                    "output": None,
                },
                {
                    "input": "温泉",
                    "output": None,
                },
                {
                    "input": "USJ",
                    "output": "osaka",
                },
                {
                    "input": "東京タワー",
                    "output": "tokyo",
                },
                {
                    "input": "南部鉄器",
                    "output": "iwate",
                },
            ]
            example_get_location_prompt = PromptTemplate(
                input_variables=["input", "output"],
                template="landmark: {input}\n prefecture: {output}",
            )
            get_address_prompt = FewShotPromptTemplate(
                input_variables=["content"],
                examples=example_get_location,
                example_prompt=example_get_location_prompt,
                prefix="""
                    あなたへの指示:
                    Userの発言が与えられる。Userの発言には、地名、観光地名、場所名、ランドマーク、伝統工芸品、シンボルなどが含まれている場合がある。
                    その地名、観光地名、場所名、ランドマーク、伝統工芸品、シンボルなどを抽出し、それが存在する都道府県名をローマ字で出力しなさい。
                    抽出できない場合は、Noneと出力しなさい。
                    ## 注意
                    - 出力する都道府県名は、ローマ字で出力しなさい。
                """,
                suffix="landmark: {content}\n prefecture:",
            )
            self.get_address_chain = LLMChain(
                llm=llm,
                prompt=get_address_prompt,
            )

    def export_prefecture_address(self, message):
        getaddress_chain = SimpleSequentialChain(
            chains=[
                self.chain1.get_landmark_chain,
                self.chain2.get_address_chain,
            ]
        )
        prefecture = getaddress_chain.run(message)
        return prefecture
