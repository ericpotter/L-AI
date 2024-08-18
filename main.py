import chain
import data
import gradio as gr
import chat
from functools import partial

# Initial state
state = {'info_base': data.PersonalInfoBase}
chat_history = [[None, "您好，我是AI中醫諮詢系統L AI，請問今天有需要諮詢嗎？"]]


# Function to generate responses using chat_gen
def get_response(message, history):
    global state

    # Call the chat_gen function to get the response
    chat_generator = chat.chat_gen(message, history, state=state)
    response = None
    for resp in chat_generator:
        response = resp

    # Update the chat history
    history.append((message, response))

    return history, history


def main():
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot()

        with gr.Row():
            text = gr.Textbox(
                show_label=False,
                placeholder="請輸入......",
            ).style(container=False)

        # Bind the submit action of the Textbox to the get_response function
        text.submit(partial(get_response), [text, chatbot], [chatbot, state])

    demo.launch()


if __name__ == '__main__':
    main()
