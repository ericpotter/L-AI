from langchain_core.prompts import ChatPromptTemplate

# 聊天機器人的提示模板
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are L AI, a Chinese medicine diagnosis robot. You are going to assist in consultation."
        "Based on the currently retrieved information: {context}, you can only ask questions about the unknown information in order."
        "Ask at most one questions at a time"
        "全部使用繁體中文"
        "Please chat with them! Stay concise, clear and polite!"
        "Your running knowledge base is: {info_base}."
        "This is for you only; Do not mention it!"
        "Do not ask them any other personal information"
        "The checking happens automatically; you cannot check manually."
    )),
    ("assistant", "{output}"),
    ("user", "{input}"),
])

# 解析器提示模板
parser_prompt = ChatPromptTemplate.from_template(
    "You are a chat assistant, and are trying to track information about the conversation."
    "You have just received a message from the user. Please fill in the schema based on the chat."
    "\n\n{format_instructions}"
    "\n\nOLD KNOWLEDGE BASE: {info_base}"
    "\n\nASSISTANT RESPONSE: {output}"
    "\n\nUSER MESSAGE: {input}"
    "\n\nNEW KNOWLEDGE BASE: "
)