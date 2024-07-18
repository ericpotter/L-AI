import opencc

converter = opencc.OpenCC('s2t')  

def is_traditional_chinese_or_digit(text):
    converted_text = converter.convert(text)
    return all('\u4e00' <= char <= '\u9fff' or char.isdigit() for char in text), converted_text

test_cases = [
    "你好",        # 繁体中文
    "你好123",     # 繁体中文和数字
    "你好123简体",  # 简体中文
    "123456",      # 只有数字
    "Hello123"     # 英文和数字
]

for text in test_cases:
    contains_traditional_chinese, converted_text = is_traditional_chinese_or_digit(text)
    print(f"Text: {text} -> Contains Traditional Chinese: {contains_traditional_chinese}, Converted Text: {converted_text}")
