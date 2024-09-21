from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import model  # 假設這個模組包含已初始化的語言模型

# 初始化語言模型
llm = model.model

# 定義症狀對應的臟器和藥材權重
physiological_symptoms = {
    "口苦": "肝",
    "頭暈": "肝",
    "容易口渴": "脾",
    "口乾": "脾",
    "消化問題": "脾",
    "排便問題": "脾",
    "容易小便": "腎",
    "水腫": "腎",
    "尿急": "腎",
    "尿液顏色不正常": "腎",
}

psychological_symptoms = {
    "過度興奮": "心",
    "開心": "心",
    "易怒": "肝",
    "容易憂思": "脾",
    "傷心過度": "肺",
    "容易受驚嚇": "腎",
}

herb_weights = {
    "天王補心丹": {"肝": 0.2, "心": 1.0, "脾": 0.2, "肺": 0.0, "腎": 0.2},
    "歸脾湯": {"肝": 0.4, "心": 0.6, "脾": 1.0, "肺": 0.1, "腎": 0.3},
    "養心湯": {"肝": 0.2, "心": 1.0, "脾": 0.4, "肺": 0.2, "腎": 0.6},
    "溫膽湯": {"肝": 1.0, "心": 0.5, "脾": 0.5, "肺": 0.1, "腎": 0.7},
    "加味逍遙散": {"肝": 1.0, "心": 0.6, "脾": 0.3, "肺": 0.1, "腎": 0.5},
    "甘麥大棗湯": {"肝": 0.8, "心": 0.6, "脾": 0.6, "肺": 0.1, "腎": 0.3},
    "孔聖枕中丹": {"肝": 0.2, "心": 1.0, "脾": 0.2, "肺": 0.1, "腎": 0.8},
    "酸棗仁湯": {"肝": 0.4, "心": 1.0, "脾": 0.3, "肺": 0.1, "腎": 0.8},
    "抑肝散": {"肝": 1.0, "心": 0.6, "脾": 0.6, "肺": 0.1, "腎": 0.4},
    "柴胡加龍骨牡蠣湯": {"肝": 0.3, "心": 0.5, "脾": 0.2, "肺": 0.2, "腎": 0.5},
}

# 定義診斷提示模板
diagnosis_template = PromptTemplate(
    input_variables=["symptom_analysis", "herb_scores"],
    template="""
        基於以下對症狀的分析和計算結果：
        {symptom_analysis}
        
        各藥材的總得分如下：
        {herb_scores}
        
        請選出得分最高的藥材，並解釋推薦理由。
    """
)

# 創建診斷鏈（LLMChain）
diagnosis_chain = LLMChain(llm=llm, prompt=diagnosis_template)

# 接收輸入的症狀
initial_input = input("請輸入患者的所有症狀，用頓號（、）分隔：")
symptom_list = initial_input.split('、')

# 進行症狀與臟器的對應
organ_scores = {"肝": 0, "心": 0, "脾": 0, "肺": 0, "腎": 0}

for symptom in symptom_list:
    symptom = symptom.strip()
    if symptom in physiological_symptoms:
        organ = physiological_symptoms[symptom]
        organ_scores[organ] += 1
    if symptom in psychological_symptoms:
        organ = psychological_symptoms[symptom]
        organ_scores[organ] += 1

# 檢查是否有匹配的症狀
if sum(organ_scores.values()) == 0:
    print("未能根據症狀判斷相關臟器，請檢查輸入的症狀。")
else:
    # 計算每個藥材的總得分
    herb_scores_dict = {}
    for herb, weights in herb_weights.items():
        score = 0
        for organ, weight in weights.items():
            score += organ_scores[organ] * weight
        herb_scores_dict[herb] = score

    # 構建症狀分析和藥材得分的字串，供模型使用
    symptom_analysis = "症狀與臟器的對應關係和得分：\n"
    for organ, score in organ_scores.items():
        symptom_analysis += f"{organ}: {score}\n"

    herb_scores = ""
    for herb, score in herb_scores_dict.items():
        herb_scores += f"{herb}: {score}\n"

    # 執行診斷鏈
    result = diagnosis_chain.run(symptom_analysis=symptom_analysis, herb_scores=herb_scores)
    print(f"AI 的診斷結果：\n{result}")