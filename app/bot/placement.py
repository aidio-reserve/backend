from app import settings
from geopy.geocoders import Nominatim
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate, FewShotPromptTemplate

OPENAI_API_KEY = settings.OPENAI_API_KEY

chat = ChatOpenAI(model="gpt-4o-mini")


def export_conversation_landmark(history):
    example_landmark_conversion = [
        {
            "input": "[('User', 'こんばんは！ location:None'), ('Concierge', 'Userさん、こんばんは”旅行の計画はお決まりですか？もしまだなら、日本国内での観光地を提案させていただきます。例えば、京都や沖縄などがおすすめです。行きたい場所や旅行の期間など、詳細を教えていただけますか？お手伝いさせてください。location:京都・沖縄'), ('User', '温泉旅行に行きたい location:None'), ('Concierge', '温泉旅行に行きたいのですね。日本国内でおすすめの温泉地は、山口県の「下関市」です。美しい景色と温泉でリラックスできます。いつからいつまで旅行される予定ですか？もしホテルの手配が必要でしたらお手伝いします。location:下関市')]",
            "output": "下関市",
        },
        {
            "input": "[('User', 'こんばんは！ location:None'), ('Concierge', 'こんばんは、私はあなたの旅行をサポートするコンシェルジュです。旅行の日程やご希望などはございますか？ location:None')]",
            "output": None,
        },
        {
            "input": "[('User', '出張で札幌市内に泊まることになりました。予算1泊10000円以内でビジネスホテルはありますか？ location:札幌市'), ('Concierge', '出張 で札幌市内に泊まるんですね。予算1泊10000円以内でビジネスホテルをお探しですね。札幌市内には便利な立地のビジネスホテルがいくつかあります。また、札幌市内には観光名所もたくさんありますので、お時間があれば観光もおすすめです。いつからいつまでの出張なのか、教えていただけますか？location:札幌市内')]",
            "output": "札幌市",
        },
    ]
    example_landmark_conversion_prompt = PromptTemplate(
        input_variables=["input", "output"],
        template="会話履歴: {input}\n location: {output}",
    )
    make_landmark_prompt = FewShotPromptTemplate(
        examples=example_landmark_conversion,
        example_prompt=example_landmark_conversion_prompt,
        input_variables=["history"],
        prefix="""
                以下の会話から、Userが最も行きたがっていると言及している一つの場所を特定してください。もし複数の場所が言及されている場合は、最も熱心に話されている場所を選んでください。
                抽出できなければ、Noneを出力しなさい。
                ## 注意
                - Userの発言は、'User' で始まる。
                - Conciergeの発言は、'Concierge' で始まる。
                - それぞれの発言の最後には、発言に含まれる場所地名、観光地名、場所名、ランドマーク、シンボルなどの情報が記載された「location:」に続く文字列が提供されている。
                - 会話の履歴は最後の発言が最新である。
                - 最新の発言を優先して抽出する。
            """,
        suffix="会話履歴: {history}\n location:",
    )
    make_landmark_chain = LLMChain(
        llm=chat,
        prompt=make_landmark_prompt,
    )

    return make_landmark_chain.run(history=history)


def export_letitude_longitude(landmark: str):
    if landmark is None:
        return None
    geolocator = Nominatim(user_agent="test")
    location = geolocator.geocode(str(landmark))
    if location is None:
        return None
    return location.latitude, location.longitude
