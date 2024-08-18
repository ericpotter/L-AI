from functools import partial
from langchain_core.runnables import RunnableLambda
from langchain.schema.runnable.passthrough import RunnableAssign
from langchain.output_parsers import PydanticOutputParser
import opencc

# Utility function for printing status
def RPrint(preface="Status: "):
    def print_and_return(x, preface=""):
        print(f"{preface}{x}")
        return x

    return RunnableLambda(partial(print_and_return, preface=preface))


# Function to extract information using Pydantic model and LLM
def RExtract(pydantic_class, llm, prompt):
    # Create a parser for the Pydantic model
    parser = PydanticOutputParser(pydantic_object=pydantic_class)

    # Assign format instructions for the prompt
    instruct_merge = RunnableAssign({
        'format_instructions': lambda x: parser.get_format_instructions()
    })

    # Function to preprocess the string before parsing
    def preparse(string):
        if '{' not in string:
            string = '{' + string
        if '}' not in string:
            string = string + '}'
        string = string.replace("\\_", "_").replace("\n", " ").replace("]", "]").replace("[", "[")
        return string

    # Return the composed runnable pipeline
    return instruct_merge | prompt | llm | preparse | parser

# 初始化 OpenCC 繁體轉換器
converter = opencc.OpenCC('s2t')

def ensure_zhtw(text):
    # 將輸入文本轉換為繁體中文
    return converter.convert(text)