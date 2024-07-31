import os
from os.path import join, dirname
from dotenv import load_dotenv

# .envファイルのパスを指定
dotenv_path = join(dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")