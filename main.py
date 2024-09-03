import data
import gradio as gr
import chain

# 初始狀態
state = {'info_base': data.PersonalInfoBase}
chat_history = [
    [None, "您好，我是AI中醫問診系統L AI，請問今天有需要諮詢嗎？"],
]

def chat_gen(message, history=[]):
    global state

    # 更新狀態，加入新的輸入和對話歷史
    state['input'] = message
    state['history'] = history
    state['output'] = "" if not history else history[-1][1]

    # Generate the new state using the internal chain
    state = chain.internal_chain.invoke(state)
    context = state.get('context')
    print(context)

    # 使用 router_chain 根據 context 判斷並生成問題
    questions = chain.questions_chain.run({"input": context})

    # 將生成的問題放入 external_chain 進行最終處理
    state['question'] = questions
    buffer = ""
    for token in chain.external_chain.stream(state):
        buffer += token
        yield buffer

    # 更新對話歷史和狀態
    ai_response = buffer.strip()
    history.append([message, ai_response])

    # 過濾並打印狀態（不包含 'history'）
    filtered_state = {k: v for k, v in state.items() if k != "history"}
    print("State after chain run:", filtered_state)

def main():
    with gr.Blocks() as demo:
        gr.Markdown("L AI 中醫問診系統")
        chatbot = gr.Chatbot(
            value=chat_history,  # 初始對話歷史
            placeholder="請輸入..."
        )
        gr.ChatInterface(chat_gen, chatbot=chatbot)

    demo.launch()

if __name__ == '__main__':
    main()