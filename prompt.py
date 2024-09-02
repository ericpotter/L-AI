from langchain_core.prompts import ChatPromptTemplate

# main chatbot prompt
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are L AI, a Chinese medicine data collecting robot. Your role is to consult with patients to understand their health condition, not diagnose."
        "Your running knowledge base is: {info_base}."
        "Use traditional chinese only"
        "You don't have the ability to answer any questions not related to your consultation"
        "Please chat with them! Stay concise, clear and polite!"
        "If they don't understand the question, explain to them"
        "This is for you only; Do not mention it!"
        "Do not ask them any other personal information"
        "The checking happens automatically; you cannot check manually."
    )),
    ("assistant", "{output}"),
    ("user", "{input}"),
])

# check whether user wants to consult
intent_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Determine if the user wants further health consultation based on the input."
        "Only answer \"yes\" or \"no\"."
    )),
    ("user", "{input}"),
])

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
