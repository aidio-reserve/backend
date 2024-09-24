import requests
import json
import os

from models import (
    save_store,
    save_config,
    save_user_info,
    load_store,
    load_config,
    load_user_info,
)


def get_hotelinfo_from_api(thread_id: str) -> dict:
    user_info = load_user_info(thread_id)
    condisions = user_info.get_thread_info()
    params = {
        "applicationId": os.environ.get("RAKUTEN_TRAVEL_API_KEY"),
        "roomNum": condisions["hotellist"].get("roomNum"),
        "adultNum": condisions["hotellist"].get("adultNum"),
        "maxCharge": condisions["hotellist"].get("maxCharge"),
        "minCharge": condisions["hotellist"].get("minCharge"),
        "checkinDate": condisions["hotellist"].get("checkinDate"),
        "checkoutDate": condisions["hotellist"].get("checkoutDate"),
        "latitude": condisions["hotellist"].get("latitude"),
        "longitude": condisions["hotellist"].get("longitude"),
        "searchRadius": 1,
        "datumType": 1,
        "sort": "-roomCharge",
    }

    # Noneでないパラメータのみをdataに追加
    data = {k: v for k, v in params.items() if v is not None}

    # POSTリクエストを送信
    url = os.environ.get("RAKUTEN_TRAVEL_API_URL")
    response = requests.post(url, json=data)
    res_json = response.json()

    return res_json


def extract_hotelinfo(hoteldata_json: dict):
    hotels_info = []
    for hotel_entry in hoteldata_json.get("hotels", []):
        hotel_data = hotel_entry.get("hotel", [])
        hotel_basic_info = hotel_data[0].get("hotelBasicInfo", {})

        # 施設名称
        hotel_name = hotel_basic_info.get("hotelName")
        # 施設画像
        hotel_image = hotel_basic_info.get("hotelImageUrl")
        # 最安値
        min_charge = hotel_basic_info.get("hotelMinCharge")
        # 評価★の数
        review_average = hotel_basic_info.get("reviewAverage")
        # 住所
        address = f"{hotel_basic_info.get('address1', '')} {hotel_basic_info.get('address2', '')}"
        # 電話番号
        phone_number = hotel_basic_info.get("telephoneNo")
        # 施設へのアクセス
        access = hotel_basic_info.get("access")
        # 駐車場情報
        parking_info = hotel_basic_info.get("parkingInformation")
        # 施設提供地図画像
        map_image = hotel_basic_info.get("hotelMapImageUrl")
        # 部屋画像
        room_image = hotel_basic_info.get("roomImageUrl")
        # お客様の声
        user_review = hotel_basic_info.get("userReview")
        # チェックイン時刻・チェックアウト時刻（データがない場合は"情報なし"とする）
        checkin_time = hotel_basic_info.get("checkinTime", "No information")
        checkout_time = hotel_basic_info.get("checkoutTime", "No information")

        # 夕食有無・朝食有無を判定
        has_dinner = False
        has_breakfast = False
        for room_entry in hotel_data[1:]:
            room_info_list = room_entry.get("roomInfo", [])
            for room_info in room_info_list:
                room_basic_info = room_info.get("roomBasicInfo", {})
                if room_basic_info.get("withDinnerFlag") == 1:
                    has_dinner = True
                if room_basic_info.get("withBreakfastFlag") == 1:
                    has_breakfast = True

        hotel_info = {
            "hotelname": hotel_name,
            "hotelimage": hotel_image,
            "minimumcharge": min_charge,
            "reviewaverage": review_average,
            "address": address.strip(),
            "phonenumber": phone_number,
            "access": access,
            "parkinginformation": parking_info,
            "hotelmapimage": map_image,
            "roomimage": room_image,
            "userreview": user_review,
            "checkintime": checkin_time,
            "checkouttime": checkout_time,
            "dinnerincluded": has_dinner,
            "breakfastincluded": has_breakfast,
        }
        hotels_info.append(hotel_info)
    return hotels_info


def get_hotelinfo_display(thread_id: str) -> dict:
    hoteldata_json = get_hotelinfo_from_api(thread_id)
    hotels_info = extract_hotelinfo(hoteldata_json)
    return hotels_info
