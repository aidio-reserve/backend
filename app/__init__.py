# __init__.py

from flask import Flask
from .views import chatbot_response, get_chat_history, on_chat_start

app = Flask(__name__)
app.route("/chatbot", methods=["POST"])(chatbot_response)
app.route("/history", methods=["GET"])(get_chat_history)
app.route("/start", methods=["POST"])(on_chat_start)
