from dotenv import load_dotenv
import os
import getpass
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

def geminiModel():
    load_dotenv()
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("請提供您的 Google API Key")
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    return model

model = geminiModel()
instruct_llm = model | StrOutputParser()
chat_llm = model | StrOutputParser()