from schemas import User_info

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.chat import ChatPromptTemplate

import settings


class MakeChatbotResponse:
    def __init__(self, user_info: User_info):
        self.user_info = user_info
        self.llm = OpenAI(model_name="gpt-3.5-turbo", api_key=settings.OPENAI_API_KEY)

    def make_chatbot_response(self):

        prompt = PromptTemplate.from_template(
            """
                あなたは"user"の旅行プランの決定、ホテルの予約をサポートする"chatbot"です。
            
                現在のホテルの条件リスト:
                {hotel_conditions}
            
                会話履歴:
                {chat_history}
            """
        )

        prompt.format(
            hotel_conditions=self.user_info.hotellist,
            chat_history=self.user_info.conversation_history,
        )

        res = self.llm.predict(prompt)

        return self.chat_model(prompt)

    def run(self):
        return self.make_chatbot_response()
