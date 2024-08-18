import data
import gradio as gr
import chain

# Initial state
state = {'info_base': data.PersonalInfoBase}
chat_history = [[None, "您好，我是AI中醫諮詢系統L AI，請問今天有需要諮詢嗎？"]]

def chat_gen(message, history=[], return_buffer=True):

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

    # Stream the results and return either the buffer or individual tokens
    buffer = ""
    for token in chain.external_chain.stream(state):
        buffer += token
        yield buffer if return_buffer else token

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
