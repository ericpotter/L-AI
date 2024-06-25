from llama_index.llms.gemini import Gemini
from llama_index.core.llms import ChatMessage


GEMINI_API = "AIzaSyCm_oSJx6H1TCdrkjyzG9aG5RPjGoV_CZQ"

# Complete
response = Gemini(
    api_key=GEMINI_API,
    model_name="models/gemini-1.5-pro-latest",
    temperature=0.6,
    max_tokens=1024
).complete("誰是王建民？")

print(response)

# Chat
messages = [
    ChatMessage(role="user", content="誰是王建民？"),
    ChatMessage(role="assistant", content="王建民是臺灣職業棒球運動員，擔任投手，在美國職棒大聯盟9個球季累計68勝。"),
    ChatMessage(role="user", content="他是哪裡人？"),
]
response = Gemini(api_key=GEMINI_API).chat(messages)
print(response)
# assistant: 臺南市   王建民於1980年3月31日出生於臺灣臺南市。

# Streaming complete (串流的方式)
response = Gemini(api_key=GEMINI_API).stream_complete("誰是王建民？")
for r in response:
    print(r.text, end="")
