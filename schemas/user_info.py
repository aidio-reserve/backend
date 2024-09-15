from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Optional
from datetime import datetime
import googlemaps
import settings
import os

# 都道府県とその県庁所在地のマッピング
prefecture_capitals = {
    "北海道": "札幌市",
    "青森県": "青森市",
    "岩手県": "盛岡市",
    "宮城県": "仙台市",
    "秋田県": "秋田市",
    "山形県": "山形市",
    "福島県": "福島市",
    "茨城県": "水戸市",
    "栃木県": "宇都宮市",
    "群馬県": "前橋市",
    "埼玉県": "さいたま市",
    "千葉県": "千葉市",
    "東京都": "新宿区",
    "神奈川県": "横浜市",
    "新潟県": "新潟市",
    "富山県": "富山市",
    "石川県": "金沢市",
    "福井県": "福井市",
    "山梨県": "甲府市",
    "長野県": "長野市",
    "岐阜県": "岐阜市",
    "静岡県": "静岡市",
    "愛知県": "名古屋市",
    "三重県": "津市",
    "滋賀県": "大津市",
    "京都府": "京都市",
    "大阪府": "大阪市",
    "兵庫県": "神戸市",
    "奈良県": "奈良市",
    "和歌山県": "和歌山市",
    "鳥取県": "鳥取市",
    "島根県": "松江市",
    "岡山県": "岡山市",
    "広島県": "広島市",
    "山口県": "山口市",
    "徳島県": "徳島市",
    "香川県": "高松市",
    "愛媛県": "松山市",
    "高知県": "高知市",
    "福岡県": "福岡市",
    "佐賀県": "佐賀市",
    "長崎県": "長崎市",
    "熊本県": "熊本市",
    "大分県": "大分市",
    "宮崎県": "宮崎市",
    "鹿児島県": "鹿児島市",
    "沖縄県": "那覇市",
}


class HotelConditions(BaseModel):
    """ホテルの条件リストを示すクラス"""

    pref: Optional[str] = Field(
        default=None,
        description="質問者が旅行で宿泊したい場所の都道府県名を示す文字列。例: '東京都','北海道','京都府','広島県'",
    )
    city: Optional[str] = Field(
        default=None,
        description="質問者が旅行で宿泊したい場所の市区町村名を示す文字列。都道府県のみが与えられている場合は、その都道府県の県庁所在地が位置する市区町村名。",
    )
    landmark: Optional[str] = Field(
        default=None,
        description="質問者が旅行で宿泊したい場所の特定のランドマークを示す文字列。",
    )
    checkinDate: Optional[str] = Field(
        default=None,
        description=f"質問者が旅行で宿泊する予定のチェックイン日を示す文字列 (YYYY-MM-DD形式)。今日以降の日付を指定してください。今日の日付は「{datetime.today().date()}」です。",
    )
    checkoutDate: Optional[str] = Field(
        default=None,
        description=f"質問者が旅行で宿泊する予定のチェックアウト日を示す文字列 (YYYY-MM-DD形式)。チェックイン日より後かつ今日以降の日付を指定してください。今日の日付は「{datetime.today().date()}」です。",
    )
    adultnNum: Optional[int] = Field(
        default=2, description="質問者の旅行で宿泊する大人の人数を示す整数。"
    )
    upClassNum: Optional[int] = Field(
        default=0,
        description="質問者の旅行で宿泊する小学生高学年（おおむね10歳～12歳）の人数を示す整数。",
    )
    lowClassNum: Optional[int] = Field(
        default=0,
        description="質問者の旅行で宿泊する小学生低学年（おおむね6歳～9歳）の人数を示す整数。",
    )
    infantWithMBNum: Optional[int] = Field(
        default=0,
        description="質問者の旅行で食事と布団付きで宿泊する幼児の人数を示す整数。",
    )
    infantWithMNum: Optional[int] = Field(
        default=0,
        description="質問者の旅行で食事のみ付きで宿泊する幼児の人数を示す整数。",
    )
    infantWithBNum: Optional[int] = Field(
        default=0,
        description="質問者の旅行で布団のみ付きで宿泊する幼児の人数を示す整数。",
    )
    infantWithNoneNum: Optional[int] = Field(
        default=0,
        description="質問者の旅行で食事および布団が不要な幼児の人数を示す整数。",
    )
    roomNum: Optional[int] = Field(
        default=1, description="質問者の旅行で宿泊する部屋の数を示す整数。"
    )
    maxCharge: Optional[int] = Field(
        default=None, description="質問者の旅行の宿泊料金の上限金額、予算を示す整数。"
    )
    minCharge: Optional[int] = Field(
        default=0, description="質問者の旅行の宿泊料金の下限金額を示す整数。"
    )


def fetch_coordinates(hotels: HotelConditions) -> dict:
    """
    ホテルの条件に基づいて座標を取得する。

    この関数は、ホテルの都道府県、市、ランドマークの情報を使用して
    Google Maps APIを呼び出し、該当する座標（緯度と経度）を取得します。
    都道府県または市の情報が不足している場合、Noneを返します。

    Args:
        hotels (HotelConditions): ホテルの条件を含むオブジェクト。

    Returns:
        dict: 座標を含む辞書。キーは "latitude" と "longitude"。
              情報が不足している場合は、両方とも None。
    """
    if hotels.pref is None or hotels.city is None:
        return {"latitude": None, "longitude": None}

    # Google Maps APIクライアントを初期化
    gm = googlemaps.Client(key=os.environ["GOOGLE_MAP_API_KEY"])

    # ホテルの情報を使用してジオコーディングを実行
    address_components = [hotels.pref, hotels.city, hotels.landmark]
    address = " ".join(filter(None, address_components))
    res = gm.geocode(address)

    # 座標を抽出して返す
    if res:
        return {
            "latitude": res[0]["geometry"]["location"]["lat"],
            "longitude": res[0]["geometry"]["location"]["lng"],
        }
    else:
        return {"latitude": None, "longitude": None}


class UserInfo(BaseModel):
    """
    ユーザー情報を管理するクラス。

    Attributes:
        thread_id (str): スレッドを識別するID。
        hotel_conditions (HotelConditions): ホテルの条件を含むオブジェクト。
        latitude (Optional[float]): ホテルの緯度。
        longitude (Optional[float]): ホテルの経度。
    """

    thread_id: str
    hotel_conditions: HotelConditions
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def update_userinfo(self, hotel_conditions: HotelConditions):
        """
        ユーザー情報を更新し、座標を取得する。

        Args:
            hotel_conditions (HotelConditions): 更新するホテルの条件。
        """
        # ホテル条件を更新
        self.hotel_conditions = hotel_conditions
        # エラーハンドリング関数を実行
        self.handle_error_conditions()
        # 座標を取得
        coordinates = fetch_coordinates(self.hotel_conditions)
        self.latitude = coordinates.get("latitude")
        self.longitude = coordinates.get("longitude")

    def handle_error_conditions(self):
        """
        エラーハンドリングの関数をまとめた関数。
        """
        self.set_city_to_prefecture_capital()
        self.validate_checkin_date()
        self.validate_checkout_date()

    def set_city_to_prefecture_capital(self):
        """
        hotel_conditions.prefに都道府県名があり、hotel_conditions.cityがNoneの場合、
        hotel_conditions.cityにその都道府県の県庁所在地を代入する。
        """
        if self.hotel_conditions.pref and not self.hotel_conditions.city:
            capital = prefecture_capitals.get(self.hotel_conditions.pref)
            if capital:
                self.hotel_conditions.city = capital

    def validate_checkin_date(self):
        """
        hotel_conditions.checkinDateが今日以前の日付の場合、Noneを代入する。
        """
        if self.hotel_conditions.checkinDate:
            try:
                checkin_date = datetime.strptime(
                    self.hotel_conditions.checkinDate, "%Y-%m-%d"
                ).date()
                today = datetime.today().date()
                if checkin_date < today:
                    self.hotel_conditions.checkinDate = None
            except ValueError:
                self.hotel_conditions.checkinDate = None

    def validate_checkout_date(self):
        """
        hotel_conditions.checkoutDateがcheckinDate以前の日付または今日以前の日付の場合、Noneを代入する。
        """
        if self.hotel_conditions.checkoutDate:
            try:
                checkout_date = datetime.strptime(
                    self.hotel_conditions.checkoutDate, "%Y-%m-%d"
                ).date()
                today = datetime.today().date()
                if self.hotel_conditions.checkinDate:
                    checkin_date = datetime.strptime(
                        self.hotel_conditions.checkinDate, "%Y-%m-%d"
                    ).date()
                else:
                    checkin_date = today
                if checkout_date <= checkin_date or checkout_date < today:
                    self.hotel_conditions.checkoutDate = None
            except ValueError:
                self.hotel_conditions.checkoutDate = None

    def get_hotel_options(self) -> dict:
        """
        ホテルのオプションを取得する。

        Returns:
            dict: ホテルのオプションを含む辞書。
        """
        # ホテルの位置情報を構築
        hotel_location = (
            "".join(
                filter(
                    None,
                    [
                        self.hotel_conditions.pref,
                        self.hotel_conditions.city,
                        self.hotel_conditions.landmark,
                    ],
                )
            )
            or None
        )
        check_in_date = self.hotel_conditions.checkinDate or None
        check_out_date = self.hotel_conditions.checkoutDate or None
        number_of_people = self.hotel_conditions.adultnNum or None
        min_charge = self.hotel_conditions.minCharge or None
        max_charge = self.hotel_conditions.maxCharge or None
        return {
            "hotel_location": hotel_location,
            "checkinDate": check_in_date,
            "checkoutDate": check_out_date,
            "number_of_people": number_of_people,
            "minCharge": min_charge,
            "maxCharge": max_charge,
        }

    def get_thread_info(self) -> dict:
        """
        スレッド情報を取得する。

        Returns:
            dict: スレッド情報を含む辞書。
        """
        return {
            "thread_id": self.thread_id,
            "hotellist": {
                **self.hotel_conditions.dict(
                    include={
                        "checkinDate",
                        "checkoutDate",
                        "adultnNum",
                        "upClassNum",
                        "lowClassNum",
                        "infantWithMBNum",
                        "infantWithMNum",
                        "infantWithBNum",
                        "infantWithNoneNum",
                        "roomNum",
                        "maxCharge",
                        "minCharge",
                    },
                ),
                "latitude": self.latitude,
                "longitude": self.longitude,
            },
        }

    def check_indispensable_values_present(self) -> bool:
        """
        latitude、longitude、checkinDate、checkoutDateのいずれかがNoneであればFalseを返し、
        そうでなければTrueを返す。

        Returns:
            bool: すべての値が存在すればTrue、いずれかがNoneであればFalse。
        """
        return all(
            [
                self.latitude is not None,
                self.longitude is not None,
                self.hotel_conditions.checkinDate is not None,
                self.hotel_conditions.checkoutDate is not None,
            ]
        )


def validate_hotel_info(user_info: UserInfo) -> str:
    """
    ユーザー情報に基づいてホテル予約に必要な情報が揃っているか確認します。

    Args:
        user_info (UserInfo): ユーザーの旅行情報を含むUserInfoオブジェクト。

    Returns:
        str: 必須情報が足りているか、または不足している情報のリストを含むメッセージ。
    """
    missing_info = []
    if user_info.latitude is None or user_info.longitude is None:
        missing_info.append("場所情報が足りていません")
    if user_info.hotel_conditions.checkinDate is None:
        missing_info.append("チェックイン日の情報が足りていません")
    if user_info.hotel_conditions.checkoutDate is None:
        missing_info.append("チェックアウト日の情報が足りていません")

    if not missing_info:
        return "必須情報はすべて与えられています。"
    return " ".join(missing_info) + " 必須情報が足りていません。"
