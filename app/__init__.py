# __init__.py

from flask import Flask
from .views import chatbot_response, on_chat_start

from .views import blueprint

app = Flask(__name__)
app.register_blueprint(blueprint)

# app.route("/chatbot", methods=["POST"])(chatbot_response)
# app.route("/start", methods=["POST"])(on_chat_start)
