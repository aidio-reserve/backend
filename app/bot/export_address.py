from .. import settings
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate, FewShotPromptTemplate

OPENAI_API_KEY = settings.OPENAI_API_KEY

chat = ChatOpenAI(model="gpt-3.5-turbo")


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


'''

class ActivateHotelinfo:

    def __init__(self):
        self.hotellist = self.Hotellist()

    class Hotellist:
        def __init__(self):
            self.middleClassCode = None
            self.smallClassCode = None
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

    def activate_hotelinfo(self, hotelinfo):
        self.hotellist.middleClassCode = hotelinfo["middleClassCode"]
        self.hotellist.smallClassCode = self.activate_smallclasscode(hotelinfo)
        self.hotellist.checkinDate = hotelinfo["checkinDate"]
        self.hotellist.checkoutDate = hotelinfo["checkoutDate"]
        self.hotellist.detailClassCode = hotelinfo["detailClassCode"]
        self.hotellist.adultNum = hotelinfo["adultNum"]
        self.hotellist.upClassNum = hotelinfo["upClassNum"]
        self.hotellist.lowClassNum = hotelinfo["lowClassNum"]
        self.hotellist.infantWithMBNum = hotelinfo["infantWithMBNum"]
        self.hotellist.infantWithMNum = hotelinfo["infantWithMNum"]
        self.hotellist.infantWithBNum = hotelinfo["infantWithBNum"]
        self.hotellist.infantWithNoneNum = hotelinfo["infantWithNoneNum"]
        self.hotellist.roomNum = hotelinfo["roomNum"]
        self.hotellist.maxCharge = hotelinfo["maxCharge"]
        self.hotellist.minCharge = hotelinfo["minCharge"]
        return self.hotellist

    def activate_smallclasscode(self, hotelinfo):
        chat = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
        prefecture = hotelinfo["middleClassCode"]
        old_smcode = hotelinfo["smallClassCode"]
        cities = areacode_list.get_smallClassCodes(prefecture)
        example_adapt_smallclasscode = [
            {
                "input": "kurashiki",
                "output": "kurashiki",
            },
            {
                "input": "箱根",
                "output": "hakone",
            },
            {
                "input": "知床",
                "output": "abashiri",
            },
            {
                "input": "hanamaki",
                "output": "kitakami",
            },
            {
                "input": "ハウステンボス",
                "output": "sasebo",
            },
            {
                "input": "none",
                "output": "none",
            },
            {
                "input": "sinjuku",
                "output": "tokyo",
            },
            {
                "input": "shibuya",
                "output": "tokyo",
            },
            {
                "input": "osaka",
                "output": "shi",
            },
            {
                "input": "kyoto",
                "output": "shi",
            },
        ]
        example_adapt_smallclasscode_prompt = PromptTemplate(
            input_variables=["input", "output"],
            template="old_smcode: {input}\n smallClassCode: {output}",
        )
        adapt_smallclasscode_prompt = FewShotPromptTemplate(
            input_variables=["smallclasscodelist", "old_smcode"],
            examples=example_adapt_smallclasscode,
            example_prompt=example_adapt_smallclasscode_prompt,
            prefix="""    
                あなたへの指示:
                現在登録されている町の名前がold_smcodeで与えられ、特定の地域のsmallClassCodeは何であるかが記載されたリストが与えられる。
                リスト内を走査して、現在登録されている町の名前から抽出した地名と最も類似する、smallClassCodeのみを出力しなさい。
                「類似する」とは日本国内の場所において、最も距離が近い、または与えられたsm_codeがリスト内のsmallClassNameに含まれていることを指す。
                ## 注意
                - old_smcodeから抽出した地名に該当するsmallClassCodeがない場合は、Noneと出力しなさい
                - 出力するのは、smallClassCodeのみである
                - smallClassCodeはリスト内シングルクォーテーションで囲まれた単語と一致するローマ字で出力しなさい 
                
                特定の地域のsmallClassCodeは何であるかが記載されたリスト:
                {smallclasscodelist}
                
                「XXXのsmallClassCodeはYYYです」の形で与えられる。XXXはold_smcode、YYYはsmallClassCodeである。
            """,
            suffix="old_smcode: {old_smcode}\n smallClassCode:",
        )
        adapt_smallclasscode_chain = LLMChain(
            llm=chat,
            prompt=adapt_smallclasscode_prompt,
        )

        if cities is None:
            return old_smcode

        if old_smcode is None:
            return old_smcode

        smallClassCode = adapt_smallclasscode_chain(
            {"smallclasscodelist": str(cities), "old_smcode": str(old_smcode)}
        )
        return str(smallClassCode)

'''
