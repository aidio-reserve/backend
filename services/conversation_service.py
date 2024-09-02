from chains import generate_ai_response, extract_hotel_info
from models import (
    save_store,
    save_config,
    save_user_info,
    load_store,
    load_config,
    load_user_info,
)


def process_message(thread_id: str, message: str) -> str:
    """
    指定されたスレッドIDとメッセージを使用してメッセージを処理し、AIのレスポンスを返す。

    この関数は以下の手順で動作します:

    1. スレッドIDに基づいてストアとユーザー情報をロード。
    2. メッセージをフォーマットし、会話履歴に追加。
    3. 会話履歴からホテル情報を抽出し、ユーザー情報を更新。
    4. AIのレスポンスを生成。
    5. 更新された会話履歴から再度ホテル情報を抽出し、ユーザー情報を更新。
    6. 更新されたユーザー情報を保存。
    7. AIのレスポンスを返却。

    Args:
        thread_id (str): スレッドを識別するID。
        message (str): ユーザーからのメッセージ。

    Returns:
        str: AIのレスポンス。
    """

    # データをロード
    store = load_store(thread_id)
    user_info = load_user_info(thread_id)

    # 会話履歴を構築
    formatted_message = f"Human: {message}"
    updated_hotel_info = extract_hotel_info(
        str(store[thread_id]) + "\n" + formatted_message
    )
    user_info.update_userinfo(updated_hotel_info)

    # AIのレスポンスを生成
    ai_response = generate_ai_response(thread_id, message)

    # 再度ストアをロードして更新された会話履歴を取得
    store = load_store(thread_id)
    updated_hotel_info = extract_hotel_info(str(store[thread_id]))
    user_info.update_userinfo(updated_hotel_info)

    # データを保存
    save_user_info(thread_id, user_info)

    return ai_response
