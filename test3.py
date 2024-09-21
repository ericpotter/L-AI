from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import model

# 初始化語言模型
llm = model.model

# 定義問診提示模板
question_template = PromptTemplate(
    input_variables=["previous_answers"],
    template="""
    患者報告睡眠不好。基於以下回答：{previous_answers}，請問應該接下來詢問什麼問題來進一步診斷？
    目前的選項是：
    1. 口腔問題 (如: 口乾, 舌苔)
    2. 食慾和排便狀況
    3. 月經問題（僅女性適用）
    4. 更年期症狀（僅適用於45歲以上女性）
    5. 心理狀況（如: 焦慮, 壓力）
    選擇一個最合適的問題進行下一步詢問。
    """
)

# 創建問診鏈（LLMChain）
diagnosis_chain = LLMChain(llm=llm, prompt=question_template)

# 創建記憶體來存儲對話狀態和診斷歷史
memory = ConversationBufferMemory()

# 初始化診斷流程
initial_answers = "患者報告睡眠不好"
memory.save_context({"previous_answers": ""}, {"answers": initial_answers})

def run_diagnosis(chain, memory):
    # 使用記憶體中已保存的上下文信息
    current_answers = memory.buffer  # 使用 buffer 屬性來獲取當前的對話歷史
    result = chain.run(current_answers)
    print(f"AI建議的下一個問題是: {result}")

    # 更新對話歷史
    new_answer = input("請輸入患者的回答: ")
    updated_answers = current_answers + f", {new_answer}"
    memory.save_context({"previous_answers": current_answers}, {"answers": updated_answers})
    return updated_answers

# 啟動診斷流程
updated_answers = run_diagnosis(diagnosis_chain, memory)

while True:
    updated_answers = run_diagnosis(diagnosis_chain, memory)
    # 根據診斷條件可以設置停止條件
    if "結束" in updated_answers:
        print("問診完成")
        break