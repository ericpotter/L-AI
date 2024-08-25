from dotenv import load_dotenv
import os
import getpass
import sources.functions as functions
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

# Set up the model
generation_config = {
    "temperature": 1.5,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

system_instruction = "only use traditional chinese to reply"

def geminiModel():
    load_dotenv()
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("請提供您的 Google API Key")
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=system_instruction
    )
    return model

model = geminiModel()
instruct_llm = model | StrOutputParser()
chat_llm = model | StrOutputParser() | functions.ensure_zhtw
check_llm = model | StrOutputParser()
