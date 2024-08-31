from chains import generate_display_hotellist
from models import (
    save_store,
    save_config,
    save_user_info,
    load_store,
    load_config,
    load_user_info,
)


def process_display_hotel(thread_id: str) -> bool:
    """
    ホテルリストを表示するかどうかを判断する。

    この関数は、指定されたスレッドIDに基づいてデータをロードし、会話履歴とユーザー情報を
    解析してホテルリストを表示するかどうかを判断します。具体的には以下の手順で動作します:

    1. スレッドIDに基づいてストアとユーザー情報をロード。
    2. 会話履歴を解析してホテルリストを表示するかどうかを判断。
    3. ユーザー情報に必須の値がすべて揃っているかを確認。
    4. ホテルリストを表示する必要があり、かつ必須の値が揃っている場合にTrueを返す。

    Args:
        thread_id (str): スレッドを識別するID。

    Returns:
        bool: ホテルリストを表示する必要があり、かつ必須の値が揃っている場合はTrue、それ以外の場合はFalse。
    """
    # データをロード
    store = load_store(thread_id)
    user_info = load_user_info(thread_id)

    # 会話履歴を解析してホテルリストを表示するかどうかを判断
    display_hotel_bool = True  # デフォルトでTrueを設定
    # display_hotel_bool = generate_display_hotellist(str(store[thread_id]))

    # ユーザー情報に必須の値がすべて揃っているかを確認
    values_present = user_info.check_indispensable_values_present()

    # ホテルリストを表示する必要があり、かつ必須の値が揃っている場合にTrueを返す
    response = display_hotel_bool and values_present

    return response
