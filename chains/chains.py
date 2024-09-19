from models import (
    save_store,
    save_config,
    save_user_info,
    load_store,
    load_config,
    load_user_info,
)
from schemas import UserInfo, HotelConditions, validate_hotel_info

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain.output_parsers import BooleanOutputParser

model_openai = ChatOpenAI(model="gpt-4o-mini")


def create_chat_prompt_template() -> ChatPromptTemplate:
    """
    チャットプロンプトテンプレートを作成する。

    この関数は、旅行サポートアシスタントのためのチャットプロンプトテンプレートを生成します。
    テンプレートは以下の指示を含むシステムメッセージを設定します:

    1. 質問者と協力して旅行プランを提案する。
    2. 目的地と宿泊するホテルの条件を決定する。
    3. 会話の流れに基づいて、旅行体験、訪問場所、旅行期間、予算などを質問者から聞き出す。
    4. 必須情報が不足している場合、それを質問者から聞き出す。
    5. 旅行体験をサポートする情報を提供する。
    6. 最新の質問者の発言に対して適切な返答を100字以内で出力する。
    7. 具体的なホテル名を示すことは禁止。

    Returns:
        ChatPromptTemplate: チャットプロンプトテンプレートオブジェクト。
    """
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "あなたは日本国内の旅行をサポートするアシスタントです。あなたの仕事は以下の通りです。"
                "質問者とあなたで協力して質問者の好む旅行のプランを提案します。決定するのは「目的地」と「宿泊するホテルの条件」です。"
                "あなたと質問者の会話の流れをもとに、どのような旅行体験を提案するか、どのような場所へ行くのか、いつからいつまで旅行に行くのか、予算などを質問者から聞き出しなさい。"
                "ホテルの条件には必須事項があります。会話の流れから、どのような情報が与えられていないかは「必須情報」で与えられるので、適宜足りていない必須情報を聞き出すようにしてください"
                "必須情報:{necessary_info}"
                "適宜、旅行体験をサポートするような情報提供を行いなさい。"
                "最新の質問者の発言に対して、適切な返答を出力しなさい。"
                "100字以内で出力しなさい。"
                "具体的なホテル名を示すのは禁止されています。",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )


def generate_ai_response(thread_id: str, message: str, store, config, user_info) -> str:
    """
    指定されたスレッドIDとメッセージを使用してAIのレスポンスを生成する。

    この関数は以下の手順で動作します:

    1. スレッドIDに基づいてストア、設定、ユーザー情報をロード。
    2. セッション履歴を取得または初期化。
    3. プロンプトテンプレートとモデルを連携。
    4. 必要なホテル情報を検証し、AIのレスポンスを生成。
    5. セッション履歴を保存。
    6. 生成されたAIのレスポンスを返却。

    Args:
        thread_id (str): スレッドを識別するID。
        message (str): ユーザーからのメッセージ。

    Returns:
        str: AIのレスポンス。
    """
    # セッション履歴を取得
    model = model_openai

    # store = load_store(thread_id)
    # config = load_config(thread_id)
    # user_info = load_user_info(thread_id)

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    # プロンプトテンプレートとモデルを連携
    prompt_template = create_chat_prompt_template()
    chain = prompt_template | model
    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="messages",
    )

    # レスポンスを生成
    necessary_info = validate_hotel_info(user_info)
    ai_response = with_message_history.invoke(
        {
            "messages": [HumanMessage(content=message)],
            "necessary_info": "".join(necessary_info),
        },
        config=config,
    )

    # セッション履歴を保存
    save_store(thread_id, store)

    return ai_response.content


def create_hotel_info_extract_prompt() -> ChatPromptTemplate:
    """
    ホテル情報を抽出するためのプロンプトテンプレートを作成する。

    この関数は、テキストから関連情報を抽出するためのプロンプトテンプレートを生成します。
    テンプレートは以下の指示を含むシステムメッセージを設定します:

    1. 抽出アルゴリズムの専門家として振る舞う。
    2. テキストから関連情報だけを抽出する。
    3. 抽出を求められた属性の値がわからない場合、その属性の値に対してNoneを返す。
    4. テキストの内容は旅行体験を望んでいる質問者と旅行エージェントであるAIの会話である。

    Returns:
        ChatPromptTemplate: ホテル情報を抽出するためのプロンプトテンプレートオブジェクト。
    """
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "あなたは抽出アルゴリズムの専門家です。"
                "テキストから関連情報だけを抽出します。"
                "抽出を求められた属性の値がわからない場合、その属性の値に対してNoneを返します。"
                "テキストの内容はある旅行体験を望んでいる質問者と、旅行エージェントであるAIの会話です。",
            ),
            ("{text}"),
        ]
    )


def extract_hotel_info(conversation_text: str) -> HotelConditions:
    """
    会話テキストからホテルの条件情報を抽出する。

    この関数は、与えられた会話テキストを解析し、ホテルの条件情報を抽出します。
    具体的には、以下の手順で動作します:

    1. モデルとプロンプトテンプレートを初期化。
    2. プロンプトテンプレートとモデルを連携し、構造化された出力を生成する設定を行う。
    3. 会話テキストを入力として、ホテルの条件情報を抽出。

    Args:
        conversation_text (str): 解析する会話テキスト。

    Returns:
        HotelConditions: 抽出されたホテルの条件情報。
    """
    model = model_openai
    hotelinfo_extract_prompt = create_hotel_info_extract_prompt()
    runnable = hotelinfo_extract_prompt | model.with_structured_output(
        schema=HotelConditions
    )
    return runnable.invoke({"text": conversation_text})


def create_display_hotellist_prompt() -> ChatPromptTemplate:
    """
    ホテルリスト表示のプロンプトテンプレートを作成する。

    この関数は、テキストの内容に基づいて質問者がホテルリストを提示してほしいかどうかを判断する
    プロンプトテンプレートを生成します。テンプレートは以下の指示を含むシステムメッセージを設定します:

    1. 文脈解釈の専門家として振る舞う。
    2. テキストの内容は旅行体験を望んでいる質問者と旅行エージェントであるAIの会話である。
    3. 質問者がホテルを提示してほしいかどうかを判断する。
    4. ホテルのリストを表示する必要がある場合、1を返し、それ以外の場合は0を返す。

    Returns:
        ChatPromptTemplate: ホテルリスト表示のプロンプトテンプレートオブジェクト。
    """
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "あなたは文脈解釈の専門家です。"
                "テキストの内容はある旅行体験を望んでいる質問者と、旅行エージェントであるAIの会話です。"
                "質問者がホテルを提示してほしいかどうかを判断してください。"
                "ホテルに関して詳細な情報が含まれている場合は、質問者がホテルを提示してほしいと思っている可能性が高いです。"
                "ホテルのリストを表示する必要がある場合、1を返し、それ以外の場合は0を返してください。",
            ),
            ("{text}"),
        ]
    )


def generate_display_hotellist(conversation_text: str) -> bool:
    """
    会話テキストからホテルリストを表示するかどうかを判断する。

    この関数は、与えられた会話テキストを解析し、質問者がホテルリストを提示してほしいかどうかを
    判断します。具体的には、以下の手順で動作します:

    1. モデルとプロンプトテンプレートを初期化。
    2. プロンプトテンプレートとモデルを連携し、構造化された出力を生成する設定を行う。
    3. 会話テキストを入力として、ホテルリストを表示するかどうかを判断。

    Args:
        conversation_text (str): 解析する会話テキスト。

    Returns:
        bool: ホテルリストを表示する必要がある場合はTrue、それ以外の場合はFalse。
    """
    model = model_openai
    display_hotellist_prompt = create_display_hotellist_prompt()
    runnable = (
        display_hotellist_prompt | model | BooleanOutputParser(true_val=1, false_val=0)
    )
    result = runnable.invoke({"text": conversation_text})
    return bool(result)
