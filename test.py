from owlready2 import *

# 創建一個新的本體（Ontology）
onto = get_ontology("http://example.org/medontology.owl")

with onto:
    # 1. 定義類別（Class）
    class Symptom(Thing):  # 症狀類別
        pass

    class Organ(Thing):  # 臟器類別
        pass

    class Herb(Thing):  # 藥材類別
        pass

    class Diagnosis(Thing):  # 診斷類別
        pass

    # 2. 定義屬性（Property）
    class AffectsOrgan(ObjectProperty):  # 定義“影響臟器”的屬性
        domain = [Symptom]  # 屬性適用於“症狀”
        range = [Organ]      # 屬性指向“臟器”

    class RecommendsHerb(ObjectProperty):  # 定義“推薦藥材”的屬性
        domain = [Diagnosis]  # 屬性適用於“診斷”
        range = [Herb]  # 屬性指向“藥材”

    class HasWeight(DataProperty):  # 定義藥材比重的屬性
        domain = [Herb]  # 屬性適用於“藥材”
        range = [float]  # 屬性是浮點數（比重）

    # 新增生理和心理層面的屬性
    class IsPhysicalSymptom(DataProperty):  # 是否為生理症狀
        domain = [Symptom]
        range = [bool]

    class IsPsychologicalSymptom(DataProperty):  # 是否為心理症狀
        domain = [Symptom]
        range = [bool]

    # 3. 創建具體的實例（Instances）
    # 臟器實例
    organ_liver = Organ("肝")
    organ_heart = Organ("心")
    organ_spleen = Organ("脾")
    organ_kidney = Organ("腎")
    organ_lung = Organ("肺")

    # 生理層面的症狀實例
    symptom_bitter_mouth = Symptom("口苦")
    symptom_bitter_mouth.IsPhysicalSymptom = True

    symptom_dizziness = Symptom("頭暈")
    symptom_dizziness.IsPhysicalSymptom = True

    symptom_dry_throat = Symptom("喉嚨乾")
    symptom_dry_throat.IsPhysicalSymptom = True

    symptom_thirsty = Symptom("口渴")
    symptom_thirsty.IsPhysicalSymptom = True

    symptom_dry_mouth = Symptom("口乾")
    symptom_dry_mouth.IsPhysicalSymptom = True

    symptom_urination_problem = Symptom("小便問題")
    symptom_urination_problem.IsPhysicalSymptom = True

    # 心理層面的症狀實例
    symptom_overjoyed = Symptom("過度開心")
    symptom_overjoyed.IsPsychologicalSymptom = True

    symptom_anger = Symptom("易怒")
    symptom_anger.IsPsychologicalSymptom = True

    symptom_depression = Symptom("憂鬱")
    symptom_depression.IsPsychologicalSymptom = True

    symptom_overthinking = Symptom("思念過頭")
    symptom_overthinking.IsPsychologicalSymptom = True

    symptom_sorrow = Symptom("過度悲傷")
    symptom_sorrow.IsPsychologicalSymptom = True

    symptom_fear = Symptom("恐懼")
    symptom_fear.IsPsychologicalSymptom = True

    symptom_easily_frightened = Symptom("容易受驚嚇")
    symptom_easily_frightened.IsPsychologicalSymptom = True

    # 藥材實例
    herb_tianwangbuxin = Herb("天王補心丹")
    herb_guipitang = Herb("歸脾湯")
    herb_yangxintang = Herb("養心湯")
    herb_wendang = Herb("溫膽湯")
    herb_jiaweixiaoyaosan = Herb("加味逍遙散")
    herb_ganmaidazao = Herb("甘麥大棗湯")
    herb_kongshengzhongdan = Herb("孔聖枕中丹")
    herb_suanzarentang = Herb("酸棗仁湯")
    herb_yigansan = Herb("抑肝散")
    herb_chaihu = Herb("柴胡加龍骨牡蠣湯")

    # 診斷實例
    diagnosis_liver = Diagnosis("肝問題診斷")
    diagnosis_spleen = Diagnosis("脾問題診斷")
    diagnosis_kidney = Diagnosis("腎問題診斷")
    diagnosis_heart = Diagnosis("心問題診斷")
    diagnosis_lung = Diagnosis("肺問題診斷")

    # 4. 設定症狀與臟器的關係
    # 生理層面的症狀與臟器關係
    symptom_bitter_mouth.AffectsOrgan = [organ_liver]
    symptom_dizziness.AffectsOrgan = [organ_liver]
    symptom_dry_throat.AffectsOrgan = [organ_liver]
    symptom_thirsty.AffectsOrgan = [organ_spleen]
    symptom_dry_mouth.AffectsOrgan = [organ_spleen]
    symptom_urination_problem.AffectsOrgan = [organ_kidney]

    # 心理層面的症狀與臟器關係
    symptom_overjoyed.AffectsOrgan = [organ_heart]
    symptom_anger.AffectsOrgan = [organ_liver]
    symptom_depression.AffectsOrgan = [organ_spleen]
    symptom_overthinking.AffectsOrgan = [organ_spleen]
    symptom_sorrow.AffectsOrgan = [organ_lung]
    symptom_fear.AffectsOrgan = [organ_kidney]
    symptom_easily_frightened.AffectsOrgan = [organ_kidney]

    # 設定診斷與推薦藥材的關係
    diagnosis_liver.RecommendsHerb = [herb_tianwangbuxin, herb_jiaweixiaoyaosan]
    diagnosis_spleen.RecommendsHerb = [herb_guipitang, herb_ganmaidazao]
    diagnosis_kidney.RecommendsHerb = [herb_yigansan, herb_chaihu]
    diagnosis_heart.RecommendsHerb = [herb_tianwangbuxin, herb_yangxintang]
    diagnosis_lung.RecommendsHerb = [herb_suanzarentang]

# 5. 保存本體到文件
onto.save(file="medontology.owl", format="rdfxml")

# 6. 查詢和推理操作
# 查詢所有標記為生理的症狀
physical_symptoms = [s for s in onto.Symptom.instances() if s.IsPhysicalSymptom]
print("生理症狀:", physical_symptoms)

# 查詢所有標記為心理的症狀
psychological_symptoms = [s for s in onto.Symptom.instances() if s.IsPsychologicalSymptom]
print("心理症狀:", psychological_symptoms)

# 基於症狀查詢影響的臟器
affected_organ_by_symptom = symptom_anger.AffectsOrgan
print(f"症狀 '{symptom_anger}' 影響的臟器:", affected_organ_by_symptom)

# 查詢診斷推薦的藥材
recommended_herbs_for_liver = diagnosis_liver.RecommendsHerb
print(f"診斷 '{diagnosis_liver}' 推薦的藥材:", [herb.name for herb in recommended_herbs_for_liver])