import data
import model
import sources.functions as functions
import prompt
from operator import itemgetter
from langchain.schema.runnable.passthrough import RunnableAssign
from langchain_core.runnables import RunnableLambda


# get and update personal data
knowbase_getter = functions.RExtract(data.PersonalInfoBase, model.instruct_llm, prompt.parser_prompt)
database_getter = RunnableLambda(itemgetter('info_base')) | data.updateData | data.getUnknownInfo

# external chain status
external_chain = prompt.chat_prompt | model.chat_llm

self_description_chain = prompt.self_description_prompt | model.chat_llm
basic_info_chain = prompt.basic_info_prompt | model.chat_llm
sleep_chain = prompt.sleeping_prompt | model.chat_llm
mouth_chain = prompt.mouth_prompt | model.chat_llm
bowel_chain = prompt.bowel_habit_prompt | model.chat_llm
period_chain = prompt.period_prompt | model.chat_llm
menopause_chain = prompt.menopause_prompt | model.chat_llm
mind_chain = prompt.mind_prompt | model.chat_llm


check_chain = prompt.check_prompt | model.check_llm

# internal chain status
internal_chain = (
    RunnableAssign({'info_base': knowbase_getter})
    | RunnableAssign({'context': database_getter})
)

