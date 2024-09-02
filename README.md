# aidio backend

aidio プロジェクトのバックエンドです。

## 技術スタック

- Python
- Flask
- Docker
- OpenAI API(LangChain)
- Google Maps API

## エンドポイント

例: `http://localhost:8000/chatting`

### `/start` (POST)

ユーザー情報の初期化

リクエストボディ:

```json
{
  "thread_id": "unique_thread_id"
}
```

レスポンス:

```json
{
  "hotellist": {
    "adultnNum": 2,
    "checkinDate": null,
    "checkoutDate": null,
    "infantWithBNum": 0,
    "infantWithMBNum": 0,
    "infantWithMNum": 0,
    "infantWithNoneNum": 0,
    "latitude": null,
    "longitude": null,
    "lowClassNum": 0,
    "maxCharge": null,
    "minCharge": 0,
    "roomNum": 1,
    "upClassNum": 0
  },
  "thread_id": "20021114"
}
```

### `/chatting` (POST)

ユーザーとの対話

リクエストボディ:

```json
{
  "thread_id": "unique_thread_id",
  "message": "user_message"
}
```

レスポンス(例):

```json
{
  "display_hotel": 1,
  "response": "AIの返答",
  "hotel_option": {
    "checkinDate": "2024-08-29",
    "checkoutDate": "2024-08-31",
    "hotel_location": "神奈川県箱根町",
    "number_of_people": 2,
    "price": "0 ~ 20000"
  }
}
```

### `/export_userinfo` (POST)

ユーザー情報のエクスポート

リクエストボディ:

```json
{
  "thread_id": "unique_thread_id"
}
```

レスポンス(例):

```json
{
  "hotellist": {
    "adultnNum": 2,
    "checkinDate": "2024-08-29",
    "checkoutDate": "2024-08-31",
    "infantWithBNum": 0,
    "infantWithMBNum": 0,
    "infantWithMNum": 0,
    "infantWithNoneNum": 0,
    "latitude": 35.232355,
    "longitude": 139.106962,
    "lowClassNum": 0,
    "maxCharge": 20000,
    "minCharge": 0,
    "roomNum": 1,
    "upClassNum": 0
  },
  "thread_id": "20021114"
}
```

## 環境変数(.env に記述)

- `OPENAI_API_KEY`: OpenAI API の API キー
- `LANGCHAIN_API_KEY`: LangChain API の API キー
- `GOOGLE_MAPS_API_KEY`: Google Maps API の API キー
