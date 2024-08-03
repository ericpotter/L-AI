import getpass
import os
from dotenv import load_dotenv
import gradio as gr

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
def RPrint(preface="狀態: "):
    def print_and_return(x, preface=""):
        print(f"{preface}{x}")
        return x
    return RunnableLambda(partial(print_and_return, preface=preface))

# 美化打印狀態的實用函數
def PPrint(preface="狀態: "):
    def print_and_return(x, preface=""):
        pprint(preface, x)
        return x
    return RunnableLambda(partial(print_and_return, preface=preface))

# 使用 Pydantic 模型和 LLM 提取信息的函數
def RExtract(pydantic_class, llm, prompt):
    parser = PydanticOutputParser(pydantic_object=pydantic_class)
    instruct_merge = RunnableAssign({'format_instructions': lambda x: parser.get_format_instructions()})
    
    def preparse(string):
        if '{' not in string: string = '{' + string
        if '}' not in string: string = string + '}'
        string = string.replace("\\_", "_").replace("\n", " ").replace("]", "]").replace("[", "[")
        return string

    return instruct_merge | prompt | llm | preparse | parser

# 個人信息的資料庫模型
class PersonalInfoBase(BaseModel):
    height: float = Field(0, description="聊天用戶的身高（厘米），如果未知則為 '0'")
    weight: float = Field(0, description="聊天用戶的體重（公斤），如果未知則為 '0'")
    gender: str = Field('unknown', description="聊天用戶的性別，如果未知則為 'unknown'")
    period: str = Field('unknown', description="聊天用戶的月經問題摘要，如果未知則為 'unknown'，如果用戶為男性則為 None")
    menopause: str = Field('unknown', description="聊天用戶是否絕經，如果未知則為 'unknown'，如果用戶為男性則為 None")
    hand_foot: str = Field('unknown', description="聊天用戶的手腳是否經常感到寒冷，如果未知則為 'unknown'")
    body: str = Field('unknown', description="聊天用戶的身體是否經常感到熱或出汗，如果未知則為 'unknown'")
    defecation: str = Field('unknown', description="聊天用戶的排便狀況摘要，如果正常則為 'normal'")
    digestive_system: str = Field('unknown', description="聊天用戶的消化系統狀況摘要，如果排便正常則為 None")
    meals: str = Field('unknown', description="聊天用戶的膳食是否正常，如果正常則為 'normal'")
    mouth: str = Field('unknown', description="聊天用戶的口腔狀況摘要，包括苦口、口乾、口臭和口渴，如果正常則為 'normal'")
    urine: str = Field('unknown', description="聊天用戶的尿液狀況摘要，如果用戶沒有口渴則為 'normal'")
    sleep: str = Field('unknown', description="聊天用戶的睡眠狀況摘要，包括睡眠時間、淺睡問題、無法入睡和早醒，如果正常則為 'normal'")
    phone: str = Field('unknown', description="聊天用戶是否在睡前使用手機，如果睡眠正常則為 None")
    stay_up: str = Field('unknown', description="聊天用戶是否經常熬夜")
    pressure: str = Field('unknown', description="聊天用戶是否承受某些壓力及其原因，如果正常則為 'normal'")
    open_problems: str = Field("", description="未知的信息")
    current_goals: str = Field("", description="代理要處理的當前目標")
    summary: str = Field("", description="對話的運行摘要。用新輸入更新這個摘要")

# 聊天機器人的提示模板
main_bot_prompt = ChatPromptTemplate.from_messages([
    ("system", "您好，我是AI中醫諮詢系統L AI，請問有什麼需要幫忙的嗎？"),
    ("assistant", "{output}"),
    ("user", "{input}"),
])

# 解析器提示模板
parser_prompt = ChatPromptTemplate.from_template(
    "您是聊天助手，並試圖跟蹤有關對話的信息。"
    "您剛剛收到了用戶的消息。請根據聊天內容填寫以下架構。"
    "\n\n{format_instructions}"
    "\n\n舊的知識庫: {info_base}"
    "\n\n助手回應: {output}"
    "\n\n用戶消息: {input}"
    "\n\n新的知識庫: "
)

# 加載環境變量
load_dotenv()

# 如果沒有設置 Google API Key，則提示輸入
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("請提供您的 Google API Key")

# 初始化語言模型
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
instruct_llm = model | StrOutputParser()
chat_llm = model | StrOutputParser()
external_chain = main_bot_prompt | chat_llm

# 獲取知識庫的函數
knowbase_getter = lambda x: PersonalInfoBase()
knowbase_getter = RExtract(PersonalInfoBase, instruct_llm, parser_prompt)

# 管理狀態的內部鏈
internal_chain = (
    RunnableAssign({'info_base': knowbase_getter})
)

# 初始化狀態
state = {'info_base': PersonalInfoBase()}

# 聊天生成函數
def chat_gen(message, history=[], return_buffer=True):
    global state
    state['input'] = message
    state['history'] = history
    state['output'] = "" if not history else history[-1][1]

    # 運行內部鏈來更新狀態
    state = internal_chain.invoke(state)
    print("鏈運行後的狀態:")
    pprint({k: v for k, v in state.items() if k != "history"})

    # 流結果
    buffer = ""
    for token in external_chain.stream(state):
        if isinstance(token, str):
            contains_traditional_chinese, converted_text = is_traditional_chinese_or_digit(token)
            if contains_traditional_chinese:
                token_output = converted_text
            else:
                token_output = token
        else:
            token_output = token
        
        buffer += token_output
        yield buffer if return_buffer else token_output

# 初始聊天歷史
chat_history = [[None, "您好，我是AI中醫諮詢系統L AI，請問有什麼需要協助的嗎？"]]

# Gradio 聊天函數
def gradio_chat(input, history):
    history.append([input, ""])
    chat_gen_obj = chat_gen(input, history)
    for output in chat_gen_obj:
        history[-1][1] = output
    return history, history

# 建立 Gradio 介面
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(value=chat_history)
    msg = gr.Textbox(placeholder="請輸入...")
    clear = gr.Button("清除")

    msg.submit(gradio_chat, [msg, chatbot], [chatbot, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False).then(lambda: "", None, msg)

# 啟動 Gradio 介面
demo.launch()