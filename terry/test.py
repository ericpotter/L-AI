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
    '心肝血虛、中樞神經興奮、神經衰弱': ['口渴', '心腹寒熱', '虛煩難寐', '高血壓', '失眠眩暈'], # 酸棗仁湯
    '神經衰弱、興奮不安、更年期、肝氣侮脾': ['失眠', '肝經虛熱', '驚悸抽搐', '腹脹食少', '睡臥不安', '嘔吐痰涎'], # 抑肝散
    '傷寒、更年期': ['血管神經性頭痛', '高血壓', '失眠', '胸滿煩驚', '身重不可轉側', '精神神經官能症'], # 柴胡加龍骨牡蠣湯
    '肝氣鬱結、痰濁内盛': ['汗吐下後虛煩不眠', '心下懊憹', '身熱不退仍散漫在表'], # 梔子豉湯
}
terms_explanation = {
    '怔忡健忘': '心裡有時候會覺得突然很慌亂，感覺心跳不正常，而且容易忘事',
    '心口多汗': '胸口靠近心臟周圍容易出汗',
    '大便或祕或溏': '大便有時候會便秘，有時候會拉肚子',
    '口舌生瘡': '嘴巴有破皮',
    '心悸虛煩': '蠻常感到心跳不正常，也異常加快，有不安的感覺，而且會覺得身體虛弱，同時又有焦慮不安的感覺',
    '驚悸盜汗': '容易受到驚嚇，晚上出汗',
    '發熱體倦': '發燒且感到疲倦',
    '食少不眠': '吃得少，睡不著',
    '神氣不寧': '感覺心裡很煩、總是坐立不安，情緒很不穩定',
    '怔忡驚悸': '心裡有時候會覺得突然很慌亂，感覺心跳不正常，容易受到驚嚇',
    '失眠多夢': '睡不著，做很多夢',
    '心悸神疲': '蠻常感到心跳不正常，也異常加快，有不安的感覺，而且感到疲倦',
    '不眠': '睡不著',
    '虛煩驚悸': '會覺得身體虛弱，同時又有焦慮不安的感覺，而且容易驚嚇',
    '口苦嘔涎': '嘴巴苦，想吐且會一直流口水',
    '膽胃不合': '感覺胃不舒服，常常有噁心、反胃的感覺，還會覺得口苦。',
    '肝胃不合': '經常覺得胃脹氣、不舒服，還會有食慾不振、噁心和打嗝的情況，有時還會覺得脾氣急躁。',
    '骨蒸勞熱': '身體裡面感覺很熱，特別是骨頭裡面，並且經常感到疲倦和虛弱，好像內熱不停地蒸騰著。',
    '咳嗽潮熱': '咳嗽且感覺身體不時會突然發熱出汗',
    '往來寒熱': '身體時冷時熱',
    '口乾便澀': '口乾且大便困難',
    '月經不調': '月經不規律',
    '血少目暗': '貧血且眼睛看東西變模糊了',
    '讀書善忘': '學習時容易忘記',
    '心神不寧': '心情總是很不穩定，感覺心裡總是不舒服，很焦慮',
    '睡眠不安': '睡眠不好，晚上總是難以入睡，而且經常醒來，睡不好',
    '精神恍惚常悲傷欲哭': '感覺腦袋有點混亂，難以集中注意力，好像沒有精神，常感到悲傷想哭',
    '歇斯底里': '情緒失控，控制不住自己的情緒，可能會大哭大笑，行為怪異',
    '言行失常': '說話和行為不正常，可能會有奇怪的言行表現',
    '呵欠頻作': '經常打呵欠',
    '口渴': '感到口乾想喝水',
    '心腹寒熱': '胃部或心臟周圍感到時冷時熱，不舒服',
    '虛煩難寐': '會覺得身體虛弱，同時又有焦慮不安的感覺，而且難以入睡',
    '高血壓': '血壓過高',
    '失眠眩暈': '睡不著且頭暈',
    '失眠': '睡不著',
    '肝經虛熱': '情緒不穩定，容易生氣或焦慮，而且消化不良，經常腹脹、食慾不振且身體發熱',
    '驚悸抽搐': '容易受到驚嚇且有抽搐',
    '腹脹食少': '腹部脹氣且食欲不振',
    '睡臥不安': '睡覺不安穩',
    '嘔吐痰涎': '嘔吐並有痰液',
    '血管神經性頭痛': '頭痛的時候感覺頭部一陣陣的疼痛，可能伴隨著頭暈或視覺模糊',
    '胸滿煩驚': '感覺胸部有種壓迫感，同時心情很焦慮，很不安',
    '身重不可轉側': '身體沉重，難以轉身',
    '精神神經官能症': '感覺身體上有各種奇怪的不適感，但醫生檢查沒有發現明顯的問題，讓我感覺很焦慮和不安',
    '汗吐下後虛煩不眠': '大量出汗、嘔吐、腹瀉後會覺得身體虛弱，同時又有焦慮不安的感覺且睡不著',
    '心下懊憹': '感覺胸部下方有一種不舒服的感覺，有時候會感到焦慮或沮喪',
    '身熱不退仍散漫在表': '發熱不退，感到散漫不集中',
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
            temp_explain=""
            for k in range(number):
                if k == number - 1: 
                    temp+=possible_symtoms[j][k]
                    temp_explain+=terms_explanation[possible_symtoms[j][k]]
                else: 
                    temp+=possible_symtoms[j][k] + "、"
                    temp_explain+=terms_explanation[possible_symtoms[j][k]] + "，"
            symtoms.append(temp)
            persona.append(temp_explain)
        index+=1


symtoms_seperate(2)            
    

data = {'ans_idx': ans_index,'cause': cause,'symptoms': symtoms,'persona': persona}

test = pd.DataFrame(data)
test.to_csv('testing2.csv', index=False)


