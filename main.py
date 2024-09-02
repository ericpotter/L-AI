import data
import gradio as gr
import chain

# Initial state
state = {'info_base': data.PersonalInfoBase}
chat_history = [
    [None, "您好，我是AI中醫問診系統L AI，請問今天有需要諮詢嗎？"],
]


def chat_gen(message, history=[]):

    # Update the state with the new input and history
    global state
    state['input'] = message
    state['history'] = history
    state['output'] = "" if not history else history[-1][1]

    # Generate the new state using the internal chain
    state = chain.internal_chain.invoke(state)

    # Filter and print the state, excluding 'history'
    print("State after chain run:")
    filtered_state = {k: v for k, v in state.items() if k != "history"}
    print(filtered_state)

    # Update chat_history with the new user input and AI response
    ai_response = state['output']
    history.append([message, ai_response])

    # Stream the results and return either the buffer or individual tokens
    buffer = ""
    for token in chain.external_chain.stream(state):
        buffer += token
    yield buffer

    # print(buffer)
    #
    # buffer = "請告訴我您的身高體重"
    #
    # # 構建一個字典來匹配 check_chain 的期望輸入格式
    # input_data = {
    #     "input": buffer,
    #     # 你可以在這裡根據需要添加更多的鍵
    #     "history": state.get("history", []),
    #     "context": state.get("context", [])
    # }
    # print(input_data)
    #
    # # 迭代 check_chain.stream() 生成器，處理 input_data 字典
    # final_output = ""
    # for token in chain.check_chain.stream(input_data):
    #     final_output += token
    #
    # # 返回最終結果
    # yield final_output

def main():
    with gr.Blocks() as demo:
        gr.Markdown("L AI")
        chatbot = gr.Chatbot(
            value=chat_history,  # Use initial chat history
            placeholder="請輸入..."
        )

        gr.ChatInterface(chat_gen, chatbot=chatbot)

    demo.launch()


if __name__ == '__main__':
    main()
