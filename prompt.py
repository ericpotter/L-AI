from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains.router.llm_router import RouterOutputParser

# main chatbot prompt
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are L AI, a Traditional Chinese Medicine Consultation robot. Your role is to ask patients' questions about their health problem"
        "The question you have to ask is: {question}"
        "If {question} is \"none\", you don't have to ask any question."
        "Use traditional chinese only"
        "You don't have the ability to answer any questions not related to Traditional Chinese Medicine"
        "Please chat with them! Stay concise, clear and polite!"
        "If they don't understand the question, explain to them"
        "This is for you only; Do not mention it!"
        "Do not ask them any other personal information"
        "The checking happens automatically; you cannot check manually."
    )),
    ("assistant", "{output}"),
    ("user", "{input}"),
])

router_template_prompt ="""Given a raw text input to a language model select the model prompt best suited for the input. \
    You will be given the names of the available prompts and a \
    description of what the prompt is best suited for. \
    You may also revise the original input if you think that revising\
    it will ultimately lead to a better response from the language model.
    
    << FORMATTING >>
    Return a markdown code snippet with a JSON object formatted to look like:
    
    \```json
    {{{{
        "destination": string \ name of the prompt to use or "DEFAULT"
        "next_inputs": string \ a potentially modified version of the original input
    }}}}
    \```
    
    REMEMBER: "destination" MUST be one of the candidate prompt \
    names specified below OR it can be "DEFAULT" if the input is not\
    well suited for any of the candidate prompts.
    REMEMBER: "next_inputs" can just be the original input \
    if you don't think any modifications are needed.
    
    << CANDIDATE PROMPTS >>
    {destinations}
    
    << INPUT >>
    {{input}}
    
    << OUTPUT (remember to include the ```json)>>"""

router_template = router_template_prompt.format(
    destinations=destinations_str
)

router_prompt = PromptTemplate(
    template=router_template_prompt,
    input_variables=["input"],
    output_parser=RouterOutputParser(),
)

# self description
self_description_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Now ask the patient to describe their health condition in their own words."
        "Only can consult their sleeping problem, if they describe others, tell them currently we don't have that function"
        "Output summary of user's problems"
    )),
    ("assistant", "請您描述一下您的身體狀況，或有任何特別不適的地方。"),
    ("assistant", "非常抱歉，目前只針對睡眠問題做諮詢，請問您有睡眠上的問題嗎？"),
])

# basic body information
basic_info_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Now ask the patient's basic information only including name, gender, height, weight, and age."
    )),
    ("assistant", "我接下來會詢問您個人健康狀況來了解您的狀況，再麻煩詳細告知，先從基本的開始，請告訴我您的名字與性別"),
    ("assistant", "請問您的身高體重，請分別用公分與公斤表示"),
])

# sleeping condition
sleeping_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Now ask about the patient's sleep quality."
    )),
    ("user", "接下來會針對睡眠問題做詢問，稍微描述一下您睡眠的情況，是否有早醒、睡不著或是淺眠的情況，也可告知您的平均的睡眠時長"),
    ("user", "容易醒來的原因是否是因為想上廁所？"),
])

# mouth condition
mouth_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Now ask about the patient's mouth condition and whether they will feel thirsty"
    )),
    ("user", "告訴我您口腔的情況，是否會口苦、口乾、口臭或是容易口渴？嘴吧是否容易破皮？"),
])

# appetite and defecation condition
appetite_defecation_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Now ask about the patient's appetite and defecation condition."
    )),
    ("user", "您的排便情況如何？是否有便秘或腹瀉的情況？"),
    ("user", "您最近食慾還正常嗎？是否有正常吃三餐"),
])

# period condition
period_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Now ask about the patient's period condition."
    )),
    ("user", "您最近月經的情況，是否正常呢？週期與疼痛狀況也可以一併告知"),
])

# menopause
menopause_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Now ask about the patient whether they have menopause symptoms."
    )),
    ("user", "您最近是否有出現更年期的症狀，例如：停經、熱潮紅、盜汗等等"),
])

# mind condition
mind_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Now ask about the patient's mind condition specially about their pressure"
    )),
    ("user", "您是否經常感覺壓力很大？您覺得是什麼樣的事情造成您的壓力"),
])

prompt_infos = [
    {
        "name": "self_description",
        "description": "Good for users to describe their health condition in their own words.",
        "prompt_template": self_description_prompt,
    },
    {
        "name": "basic_info",
        "description": "Good for collecting users' basic information including name, gender, height, weight, and age.",
        "prompt_template": basic_info_prompt,
    },
    {
        "name": "sleeping",
        "description": "Good for collecting users' sleep quality.",
        "prompt_template": sleeping_prompt,
    },
    {
        "name": "mouth",
        "description": "Good for collecting users' mouth condition.",
        "prompt_template": mouth_prompt,
    },
    {
        "name": "appetite defecation",
        "description": "Good for collecting users' appetite and defecation condition.",
        "prompt_template": appetite_defecation_prompt,
    },
]

# parser prompt
parser_prompt = ChatPromptTemplate.from_template(
    "You are a chat assistant, and are trying to track information about the conversation."
    "You have just received a message from the user. Please fill in the schema based on the chat."
    "\n\n{format_instructions}"
    "\n\nOLD KNOWLEDGE BASE: {info_base}"
    "\n\nASSISTANT RESPONSE: {output}"
    "\n\nUSER MESSAGE: {input}"
    "\n\nNEW KNOWLEDGE BASE: "
)
