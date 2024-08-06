import getpass
import os
from dotenv import load_dotenv
import gradio as gr
from operator import itemgetter

from langchain_core.messages import HumanMessage, SystemMessage, ChatMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain.schema.runnable.passthrough import RunnableAssign
from langchain.output_parsers import PydanticOutputParser

from functools import partial
from typing import List
from pydantic import BaseModel, Field

import opencc
converter = opencc.OpenCC('s2t')

# 美化打印設置
from rich.console import Console
from rich.style import Style

console = Console()
base_style = Style(color="#76B900", bold=True)
pprint = partial(console.print, style=base_style)

# 檢查文字是否為繁體中文或數字
def is_traditional_chinese_or_digit(text):    
    converted_text = converter.convert(text)
    return all('\u4e00' <= char <= '\u9fff' or char.isdigit() for char in text), converted_text

# 打印狀態的實用函數
def RPrint(preface = "狀態: "):
    def print_and_return(x, preface = ""):
        print(f"{preface}{x}")
        return x
    return RunnableLambda(partial(print_and_return, preface = preface))

# 美化打印狀態的實用函數
def PPrint(preface = "狀態: "):
    def print_and_return(x, preface = ""):
        pprint(preface, x)
        return x
    return RunnableLambda(partial(print_and_return, preface = preface))

# 使用 Pydantic 模型和 LLM 提取信息的函數
def RExtract(pydantic_class, llm, prompt):
    parser = PydanticOutputParser(pydantic_object = pydantic_class)
    instruct_merge = RunnableAssign({'format_instructions': lambda x: parser.get_format_instructions()})
    
    def preparse(string):
        if '{' not in string: string = '{' + string
        if '}' not in string: string = string + '}'
        string = string.replace("\\_", "_").replace("\n", " ").replace("]", "]").replace("[", "[")
        return string

    return instruct_merge | prompt | llm | preparse | parser

def get_info_fn(base: BaseModel) -> dict:
    '''Given a PersonalInfoBase instance, return a dictionary with relevant information.'''
    return {
        'height': base.height,
        'weight': base.weight,
        'gender': base.gender,
        'period': base.period,
        'menopause': base.menopause,
        'hand_foot': base.hand_foot,
        'body': base.body,
        'defecation': base.defecation,
        'digestive_system': base.digestive_system,
        'meals': base.meals,
        'mouth': base.mouth,
        'urine': base.urine,
        'sleep': base.sleep,
        'phone': base.phone,
        'stay_up': base.stay_up,
        'pressure': base.pressure,
    }
    
get_info = RunnableLambda(get_info_fn)

# get unkown information
def get_unknown_info(d: dict) -> str:
    required_info = ['height', 'weight', 'gender', 'period', 'menopause', 'hand_foot',
                    'body', 'defecation', 'digestive_system', 'meals', 'mouth', 'urine',
                    'sleep', 'phone', 'stay_up', 'pressure']
    unknown_info = [info for info in required_info if d[info] == 'unknown' or d[info] == 0]
    if not unknown_info:  # 如果 unknown_info 為空列表
        return "All information known"
    else:
        return "The unknown information are: " + ", ".join(unknown_info)

# 個人信息的資料庫模型
class PersonalInfoBase(BaseModel):
    
    # basic information
    height: float = Field(0, description = "聊天用戶的身高（公分），如果未知則為 '0'")
    weight: float = Field(0, description = "聊天用戶的體重（公斤），如果未知則為 '0'")
    gender: str = Field('unknown', description = "聊天用戶的性別，如果未知則為 'unknown'")
    period: str = Field('unknown', description = "聊天用戶的月經問題摘要，如果未知則為 'unknown'，如果用戶為男性則為 'none'")
    menopause: str = Field('unknown', description = "聊天用戶是否絕經，如果未知則為 'unknown'，如果用戶為男性則為 'none'")
    
    # body condition
    hand_foot: str = Field('unknown', description = "聊天用戶的手腳是否經常感到寒冷，如果正常則為 'normal'")
    body: str = Field('unknown', description = "聊天用戶的身體是否經常感到熱或出汗，如果正常則為 'normal'")
    defecation: str = Field('unknown', description = "聊天用戶的排便狀況摘要，如果整體正常則為 'normal'")
    digestive_system: str = Field('unknown', description = "聊天用戶的消化系統狀況摘要，如果排便正常則為 'none'")
    meals: str = Field('unknown', description = "聊天用戶的三餐是否正常，如果正常則為 'normal'")
    mouth: str = Field('unknown', description = "聊天用戶的口腔狀況摘要，一定包含是否口苦、口乾、口臭和口渴，如果正常則為 'normal'")
    urine: str = Field('unknown', description = "聊天用戶的尿液狀況摘要，如果用戶不會口渴則為 'normal'")
    
    # sleeping condition
    sleep: str = Field('unknown', description = "聊天用戶的睡眠狀況摘要，一定包括睡眠時間、淺睡問題、無法入睡和早醒，如果正常則為 'normal'")
    phone: str = Field('unknown', description = "聊天用戶是否在睡前使用手機，如果睡眠正常則為 'none'")
    stay_up: str = Field('unknown', description = "聊天用戶是否經常熬夜")
    pressure: str = Field('unknown', description = "聊天用戶是否承受某些壓力及其原因，如果沒有則為 'none'")
    
    # open_problems: str = Field("", description = "The unknown information")
    current_goals: str = Field("", description = "Current goal for the agent to address")

# 聊天機器人的提示模板
main_bot_prompt = ChatPromptTemplate.from_messages([
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
    "You are a chat assistant of Traditional Chinese Medicine, and are trying to track information about the conversation."
    "You have just recieved a message from the user. Please fill in the schema based on the chat."
    "\n\n{format_instructions}"
    "\n\nOLD KNOWLEDGE BASE: {info_base}"
    "\n\nASSISTANT RESPONSE: {output}"
    "\n\nUSER MESSAGE: {input}"
    "\n\nNEW KNOWLEDGE BASE: "
)

# 加載環境變量
load_dotenv()

# 如果沒有設置 Google API Key，則提示輸入
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("請提供您的 Google API Key")

# 初始化語言模型
model = ChatGoogleGenerativeAI(model = "gemini-1.5-flash")
instruct_llm = model | StrOutputParser() # 輸出結構化
chat_llm = model | StrOutputParser()
external_chain = main_bot_prompt | chat_llm

# 獲取知識庫的函數
knowbase_getter = lambda x: PersonalInfoBase()
knowbase_getter = RExtract(PersonalInfoBase, instruct_llm, parser_prompt)

database_getter = lambda x: "Not implemented"
database_getter = itemgetter('info_base') | get_info | get_unknown_info

# 管理狀態的內部鏈
internal_chain = (
    RunnableAssign({'info_base': knowbase_getter})
    | RunnableAssign({'context' : database_getter})
)

# 初始化狀態
state = {'info_base': PersonalInfoBase()}

# 聊天生成函數
def chat_gen(message, history=[], return_buffer=True):

    ## Pulling in, updating, and printing the state
    global state
    state['input'] = message
    state['history'] = history
    state['output'] = "" if not history else history[-1][1]

    ## Generating the new state from the internal chain
    state = internal_chain.invoke(state)
    print("State after chain run:")
    pprint({k:v for k,v in state.items() if k != "history"})

    ## Streaming the results
    buffer = ""
    for token in external_chain.stream(state):
        buffer += token
        yield buffer if return_buffer else token

def queue_fake_streaming_gradio(chat_stream, history = [], max_questions=8):

    ## Mimic of the gradio initialization routine, where a set of starter messages can be printed off
    for human_msg, agent_msg in history:
        if human_msg: print("\n[ Human ]:", human_msg)
        if agent_msg: print("\n[ Agent ]:", agent_msg)

    ## Mimic of the gradio loop with an initial message from the agent.
    for _ in range(max_questions):
        message = input("\n[ Human ]: ")
        print("\n[ Agent ]: ")
        history_entry = [message, ""]
        for token in chat_stream(message, history, return_buffer=False):
            print(token, end='')
            history_entry[1] += token
        history += [history_entry]
        print("\n")

# 初始聊天歷史
chat_history = [[None, "您好，我是AI中醫諮詢系統L AI，請問今天有需要諮詢嗎？"]]

## Simulating the queueing of a streaming gradio interface, using python input
queue_fake_streaming_gradio(
    chat_stream = chat_gen,
    history = chat_history
)

# # Gradio 聊天函數
# def gradio_chat(input, history):
#     history.append([input, ""])
#     chat_gen_obj = chat_gen(input, history)
#     for output in chat_gen_obj:
#         history[-1][1] = output
#     return history, history

# # 建立 Gradio 介面
# with gr.Blocks() as demo:
#     chatbot = gr.Chatbot(value=chat_history)
#     msg = gr.Textbox(placeholder="請輸入...")
#     clear = gr.Button("清除")

#     msg.submit(gradio_chat, [msg, chatbot], [chatbot, chatbot])
#     clear.click(lambda: None, None, chatbot, queue=False).then(lambda: "", None, msg)

# # 啟動 Gradio 介面
# demo.launch()