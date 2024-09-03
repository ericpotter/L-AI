import data
import model
import sources.functions as functions
import prompt
from operator import itemgetter
from langchain.schema.runnable.passthrough import RunnableAssign
from langchain_core.runnables import RunnableLambda
from langchain.chains.router import MultiPromptChain, LLMRouterChain
from langchain.chains import SequentialChain, LLMChain

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

destination_chains = {
    "self_description": LLMChain(llm=model.model, prompt=prompt.self_description_prompt),
    "basic_info": LLMChain(llm=model.model, prompt=prompt.basic_info_prompt),
    "sleeping": LLMChain(llm=model.model, prompt=prompt.sleeping_prompt),
    "mouth_condition": LLMChain(llm=model.model, prompt=prompt.mouth_prompt),
    "appetite_defecation": LLMChain(llm=model.model, prompt=prompt.appetite_defecation_prompt),
    "period_condition": LLMChain(llm=model.model, prompt=prompt.period_prompt),
    "menopause": LLMChain(llm=model.model, prompt=prompt.menopause_prompt),
    "mind_condition": LLMChain(llm=model.model, prompt=prompt.mind_prompt)
}

router_chain = LLMRouterChain.from_llm(model.model, prompt.router_prompt)
questions_chain = MultiPromptChain(router_chain=router_chain,
                         destination_chains=destination_chains,
                         default_chain=destination_chains["self_description"], verbose=True
                        )