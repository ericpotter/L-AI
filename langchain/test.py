import getpass
import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain.schema.runnable import RunnableBranch, RunnablePassthrough
from langchain.schema.runnable.passthrough import RunnableAssign
from langchain.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
from IPython.display import Markdown, display
from functools import partial
from typing import List, Union, Optional, Dict
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
            .replace("\]", "]")
            .replace("\[", "[")
        )
        # print(string)  ## Good for diagnostics
        return string
    return instruct_merge | prompt | llm | preparse | parser

# Database
class PersonalInfoBase(BaseModel):
    ## Fields of the BaseModel, which will be validated/assigned when the knowledge base is constructed
    name: str = Field('unknown', description="Chatting user's name, unknown if unknown")
    height: float = Field(0, description="Chatting user's height, 0 if unknown")
    weight: float = Field(0, description="Chatting user's weight, 0 if unknown")
    gender: str = Field('unknown', description="Chatting user's weight, unknown if unknown")
    summary: str = Field('unknown', description="Running summary of conversation. Update this with new input")
    response: str = Field('unknown', description="An ideal response to the user based on their new message")
    

# LLM Model
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Provide your Google API Key")

model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", convert_system_message_to_human=True)
instruct_llm = model | StrOutputParser()


# prompt
bot_main_prompt = ChatPromptTemplate.from_template(
    "You are chatting with a user. The user just responded ('input'). Please update the knowledge base."
    " Record your response in the 'response' tag to continue the conversation."
    " Do not hallucinate any details, and make sure the knowledge base is not redundant."
    " Update the entries frequently to adapt to the conversation flow."
    "\n{format_instructions}"
    "\n\nOLD KNOWLEDGE BASE: {info_base}"
    "\n\nNEW MESSAGE: {input}"
    "\n\nNEW KNOWLEDGE BASE:"
)

extractor = RExtract(PersonalInfoBase, instruct_llm, bot_main_prompt)
info_update = RunnableAssign({'know_base' : extractor})

## Initialize the knowledge base and see what you get
state = {'info_base' : PersonalInfoBase()}
state['input'] = "My name is Carmen Sandiego! Guess where I am! Hint: It's somewhere in the United States."
state = info_update.invoke(state)
pprint(state)