## 2024-06-12

目標

- ユーザーの発言を受け取り、どのような操作をするかを決定する
  - ホテルの条件更新をする Tool(ユーザーから変更)
    - 与えるもの: ユーザーとの会話履歴、ホテルの条件
    - 期待するもの: 最新のユーザーの発言からホテルの条件を更新するか否かを読み取り、更新する場合は関数を実行
  - 返答を作成する Tool(必須)
    - 与えるもの: ユーザーとの会話履歴、ホテルの条件
    - 期待するもの: 最新のユーザーの発言及び現在のホテルの条件リストに基づいた返答 ホテルの条件更新差分があるか否かも大事かも
  - ユーザーの会話履歴及びホテルの条件を保存する Tool(必須)
    - 与えるもの: ユーザーの発言、ホテルの条件
    - 期待するもの: ユーザーの発言及びホテルの条件を保存する 場所情報や日時情報も保存する