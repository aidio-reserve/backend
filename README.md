# バックエンドシステム

## 概要

Flask を使用して API サーバを構築

## アクセス方法

- 会話の開始  
  `http://localhost:5000/start`  
  パラメータ: thread_id(スレッド ID)
- 会話の継続  
  `http://localhost:5000/chatting`  
  パラメータ: thread_id(スレッド ID), message(ユーザのメッセージ)
- ユーザー情報取得  
  `http://localhost:5000/export_userinfo`  
  パラメータ: thread_id(スレッド ID)
