import opencc

# 初始化 OpenCC 繁體轉換器
converter = opencc.OpenCC('s2t')

def is_traditional_chinese_or_digit(text):
    converted_text = converter.convert(text)
    return all('\u4e00' <= char <= '\u9fff' or char.isdigit() for char in text), converted_text