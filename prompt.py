import data
import model.gemini as gemini
import sources.functions as functions

from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable.passthrough import RunnableAssign

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

model = gemini.geminiModel()

instruct_llm = model | StrOutputParser()
chat_llm = model | StrOutputParser()

external_chain = chat_prompt | chat_llm

PersonalInfoBase = data.convertToBaseModel('health_data/test_user.csv')

# get and update personal data
knowbase_getter = functions.RExtract(PersonalInfoBase, instruct_llm, parser_prompt)
database_getter = itemgetter('info_base') | data.getInfoDict | data.getUnknownInfo

# 管理狀態的內部鏈
internal_chain = (
    RunnableAssign({'info_base': knowbase_getter})
    | RunnableAssign({'context': database_getter})
)

# 初始化狀態
state = {'info_base': PersonalInfoBase}


chat_history = [[None, "您好，我是AI中醫諮詢系統L AI，請問今天有需要諮詢嗎？"]]

def chat_gen(message, history=[], return_buffer=True):
    # Pulling in, updating, and printing the state
    global state
    state['input'] = message
    state['history'] = history
    state['output'] = "" if not history else history[-1][1]

    # Generating the new state from the internal chain
    state = internal_chain.invoke(state)
    print("State after chain run:")
    filtered_state = {k: v for k, v in state.items() if k != "history"}
    print(filtered_state)

    # Streaming the results
    buffer = ""
    for token in external_chain.stream(state):
        buffer += token
        yield buffer if return_buffer else token

def queue_fake_streaming_gradio(chat_stream, history=[], max_questions=8):
    # Mimic of the gradio initialization routine, where a set of starter messages can be printed off
    for human_msg, agent_msg in history:
        if human_msg: print("\n[ Human ]:", human_msg)
        if agent_msg: print("\n[ Agent ]:", agent_msg)

    # Mimic of the gradio loop with an initial message from the agent.
    for _ in range(max_questions):
        message = input("\n[ Human ]: ")
        print("\n[ Agent ]: ")
        history_entry = [message, ""]
        for token in chat_stream(message, history, return_buffer=False):
            print(token, end='')
            history_entry[1] += token
        history += [history_entry]
        print("\n")

# 模擬Gradio界面，使用Python輸入
queue_fake_streaming_gradio(
    chat_stream=chat_gen,
    history=chat_history
)