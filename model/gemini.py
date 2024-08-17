from dotenv import load_dotenv
import os
import getpass

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("請提供您的 Google API Key")

model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")