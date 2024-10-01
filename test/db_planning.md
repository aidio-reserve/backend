### start エンドポイント

- 初期化 threadid をキーにして会話履歴、ユーザー情報を初期化

<h1>

### chatting エンドポイント

- ロード InMemoryChatMessageHistory ← ここに今までの会話履歴などを取得して変数にする
- ロード ユーザー情報を取得して変数にする
  - process_message メソッド中で会話履歴の更新、ユーザー情報の更新を行う
  - いちいちロードしないように、process_message 関数に会話履歴やユーザー情報の変数を渡す実装に変更
