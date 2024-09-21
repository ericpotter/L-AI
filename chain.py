import data
import model
import sources.functions as functions
import prompt
from operator import itemgetter
from langchain.schema.runnable.passthrough import RunnableAssign
from langchain_core.runnables import RunnableLambda
from langchain.chains.router import MultiPromptChain, LLMRouterChain
from langchain.chains import SequentialChain, LLMChain
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

# get and update personal data
knowbase_getter = functions.RExtract(data.PersonalInfoBase, model.instruct_llm, prompt.parser_prompt)
database_getter = RunnableLambda(itemgetter('info_base')) | data.updateData | data.getUnknownInfo

# external chain status
external_chain = prompt.chat_prompt | model.chat_llm

# internal chain status
internal_chain = (
    RunnableAssign({'info_base': knowbase_getter})
    | RunnableAssign({'context': database_getter})
)

destination_chains = {}
for p_info in prompt.prompt_infos:
    name = p_info["name"]
    prompt_template = p_info["prompt_template"]
    prompt = ChatPromptTemplate.from_template(template=prompt_template)
    chain = LLMChain(llm=model.model, prompt=prompt)
    destination_chains[name] = chain
destinations = "\n".join([f"{p['name']}: {p['description']}" for p in prompt.prompt_infos])

default_prompt = ChatPromptTemplate.from_template("{input}")
default_chain = LLMChain(llm=model.model, prompt=default_prompt)

router_chain = LLMRouterChain.from_llm(model.model, prompt.router_prompt)

chain = MultiPromptChain(router_chain=router_chain, destination_chains=destination_chains, default_chain=default_chain, verbose=True)