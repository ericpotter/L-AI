import getpass
import os
from dotenv import load_dotenv
from IPython.display import Markdown, display
import gradio as gr

from langchain_core.messages import HumanMessage, SystemMessage, ChatMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain.schema.runnable import RunnableBranch, RunnablePassthrough, RunnableMap, RunnableLambda
from langchain.schema.runnable.passthrough import RunnableAssign
from langchain.output_parsers import PydanticOutputParser

from functools import partial
from typing import List, Union, Optional, Dict, Iterable
from operator import itemgetter
from pydantic import BaseModel, Field

from rich.console import Console
from rich.style import Style
from rich.theme import Theme

console = Console()
base_style = Style(color="#76B900", bold=True)
pprint = partial(console.print, style=base_style)

# Useful Tools
def RPrint(preface="State: "):
    def print_and_return(x, preface=""):
        print(f"{preface}{x}")
        return x
    return RunnableLambda(partial(print_and_return, preface=preface))

def PPrint(preface="State: "):
    def print_and_return(x, preface=""):
        pprint(preface, x)
        return x
    return RunnableLambda(partial(print_and_return, preface=preface))

def RExtract(pydantic_class, llm, prompt):
    parser = PydanticOutputParser(pydantic_object=pydantic_class)
    instruct_merge = RunnableAssign({'format_instructions' : lambda x: parser.get_format_instructions()})
    def preparse(string):
        if '{' not in string: string = '{' + string
        if '}' not in string: string = string + '}'
        string = (string
            .replace("\\_", "_")
            .replace("\n", " ")
            .replace("]", "]")
            .replace("[", "[")
        )
        # print(string)  ## Good for diagnostics
        return string
    return instruct_merge | prompt | llm | preparse | parser

# Database
class PersonalInfoBase(BaseModel):
    # basic information
    # name: str = Field('unknown', description="Chatting user's name, unknown if unknown")
    height: float = Field(0, description="Chatting user's height in centimeter, '0' if unknown")
    weight: float = Field(0, description="Chatting user's weight in kilogram, '0' if unknown")
    gender: str = Field('unknown', description="Chatting user's weight, 'unknown' if unknown")
    period: str = Field('unknown', description="Summary of chatting user's period problems, 'unknown' if unknown, None if User is a male")
    menopause: str = Field('unknown', description="Whether chatting user have menopause, 'unknown' if unknown, None if User is a male")
    
    # common information
    hand_foot: str = Field('unknown', description="Whether chatting user's feet and hands often feel cold, 'unknown' if unknown")
    body: str = Field('unknown', description="Whether chatting user's body often feeling hot or sweaty, 'unknown' if unknown")
    defecation: str = Field('unknown', description="Summary of chatting user's defecation condition, 'normal' if normal")
    disgestive_system: str = Field('unknown', description="Summary of chatting user's disgestive system, 'None' if defecation is normal")
    
    # Meals
    meals: str = Field('unknown', description="Whether chatting user's meals is normal, 'normal' if normal")
    mouth: str = Field('unknown', description="Summary of chatting user's mouth condition including bitter mouth, dry mouth, bad breath and thirst, 'normal' if normal")
    urine: str = Field('unknown', description="Summary of chatting user's urine condition, 'normal' if user don't have thirst" )

    # sleep
    sleep: str = Field('unknown', description="Summary of chatting user's sleep condition, including sleep time, light sleep problem, can't fall asleep, and wake up early, 'normal' if normal")
    phone: str = Field('unknown', description="Whether chatting user uses cellphone before sleeping, 'None' if sleep is normal")
    
    # Stay up
    stay_up: str = Field('unknown', description="Whether chatting user often stays up")
    
    # Mental
    pressure: str = Field('unknown', description="Whether chatting user suffer from some pressure and what are the reasons, 'normal'if normal")
    
    
    open_problems: str = Field("", description="Informations that are unknown")
    current_goals: str = Field("", description="Current goal for the agent to address")
    summary: str = Field("", description="Running summary of conversation. Update this with new input")
    
    
    
# prompt
main_bot_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Your are a courteous Chinese medicine consultation chatbot named L AI."
        "Don't answer irrelevant questions regarding user's personal health"
        "Using Traditional Chinese to answer"
        "When the user wants medical consultation, only ask for their personal information one by one based on {info_base}, and give them what specific units they have to provide"
        "Your running knowledge base is: {info_base}."
        "This is for you only; Do not mention it!"
        "Don't ask the same questions"
    )),
    ("assistant", "{output}"),
    ("user", "{input}"),
])

parser_prompt = ChatPromptTemplate.from_template(
    "You are a chat assistant, and are trying to track info about the conversation."
    " You have just recieved a message from the user. Please fill in the schema based on the chat."
    "\n\n{format_instructions}"
    "\n\nOLD KNOWLEDGE BASE: {info_base}"
    "\n\nASSISTANT RESPONSE: {output}"
    "\n\nUSER MESSAGE: {input}"
    "\n\nNEW KNOWLEDGE BASE: "
)


# LLM Model & Chain
load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Provide your Google API Key")

model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
instruct_llm = model | StrOutputParser()
chat_llm = model | StrOutputParser()
external_chain = main_bot_prompt | chat_llm


knowbase_getter = lambda x: PersonalInfoBase()
knowbase_getter = RExtract(PersonalInfoBase, instruct_llm, parser_prompt)


## These components integrate to make your internal chain
internal_chain = (
    RunnableAssign({'info_base' : knowbase_getter})
)

state = {'info_base' : PersonalInfoBase()}

# Chat implementation
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

def queue_fake_streaming_gradio(chat_stream, history = [], max_questions=10):

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

# history is of format [[User response 0, Bot response 0], ...]
chat_history = [[None, "您好，我是AI中醫諮詢系統L AI，請問有什麼需要協助的嗎？"]]

# Simulating the queueing of a streaming gradio interface, using python input
queue_fake_streaming_gradio(
    chat_stream = chat_gen,
    history = chat_history
)

# chatbot = gr.Chatbot(value=[[None, "Hello! I'm your SkyFlow agent! How can I help you?"]])
# demo = gr.ChatInterface(chat_gen, chatbot=chatbot).queue().launch(debug=True, share=True)