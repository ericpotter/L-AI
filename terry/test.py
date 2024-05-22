import pandas as pd
import numpy as np
import os
from itertools import combinations
ans_index = []
cause = []
symtoms = []
persona = []


treatsments = {
    '思慮過度、心血不足': ['怔忡健忘', '心口多汗', '大便或祕或溏', '口舌生瘡', '心悸虛煩'], # 天王補心丹
    '思慮過度、勞傷心脾或脾虛': ['怔忡健忘', '驚悸盜汗', '發熱體倦', '食少不眠'], # 歸脾湯
    '心虛血少': ['神氣不寧', '怔忡驚悸', '失眠多夢', '心悸神疲'], # 養心丹
    '膽虛痰熱': ['不眠', '虛煩驚悸', '口苦嘔涎', '膽胃不合'], # 溫膽湯
    '血虛肝燥、怒氣傷肝、更年期': ['肝胃不合', '失眠多夢', '骨蒸勞熱', '咳嗽潮熱', '往來寒熱', '口乾便澀', '月經不調', '血少目暗'], # 加味逍遙散
    '腎精不足、心血不足、痰火亂其神明': ['讀書善忘', '失眠多夢', '心神不寧'], # 孔聖枕中丹
    '臟躁、心煩失眠心悸、更年期、心律不整': ['睡眠不安', '精神恍惚常悲傷欲哭', '歇斯底里', '言行失常', '呵欠頻作'], # 甘麥大棗湯
    '心肝血虛、中樞神經興奮、神經衰弱': ['口渴', '心腹寒熱', '虛煩難寐', '血壓上升', '失眠眩暈'], # 酸棗仁湯
    '神經衰弱、興奮不安、更年期障礙、肝氣侮脾': ['失眠', '肝經虛熱', '驚悸抽搐', '腹脹食少', '睡臥不安', '嘔吐痰涎'], # 抑肝散
    '傷寒、更年期': ['血管神經性頭痛', '高血壓', '失眠', '胸滿煩驚', '身重不可轉側', '精神神經官能症'], # 柴胡加龍骨牡蠣湯
    '肝氣鬱結、痰濁内盛': ['汗吐下後虛煩不眠', '心下懊憹', '身熱不退仍散漫在表'], # 梔子鼓湯
}

def symtoms_seperate(number):
    index=0
    for i in treatsments.keys():
        possible_symtoms = list(combinations(treatsments[i], number))
        amount_combination = len(possible_symtoms)
        for j in range(amount_combination):
            cause.append(i)
            ans_index.append(index)
            temp=""
            for k in range(number):
                if k == number-1: temp+=possible_symtoms[j][k]
                else: temp+=possible_symtoms[j][k] + "、"
            symtoms.append(temp)
        index+=1


symtoms_seperate(3)            
    

data = {'ans_idx': ans_index,'cause': cause,'symptoms': symtoms,}

test = pd.DataFrame(data)
test.to_csv('testing3.csv', index=False)


