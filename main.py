import data
import gradio as gr
import chain

# Initial state
state = {'info_base': data.PersonalInfoBase}
chat_history = [
    # [None, "您好，我是AI中醫問診系統L AI，請問今天有需要諮詢嗎？"],
    # ["我最近都睡不太好", "睡不好的原因可能會有很多種，為了更準確分析，我接下來會詢問您個人健康狀況來了解您的狀況，再麻煩詳細告知，先從基本的開始，請告訴我您的名字與性別"],
    # ["我姓楊，女性", "楊小姐您好，請問您的身高體重，請分別用公分與公斤表示"],
    # ["165 50", "想要詢問您最近月經的情況，是否正常呢？週期與疼痛狀況也可以一併告知"],
    # ["經期週期正常，但是有感覺比較疼痛", "了解您的情況，基本資料蒐集完成，接下來針對身體的資料作提問，想請問您平常手腳感受狀況如何？冰冷？抑或是熱？"],
    # ["會容易感受冰冷", "了解了，那身體整體的情況呢，會容易感到燥熱嗎？還是容易流汗呢？"],
    # ["都不會", "好的，那身體整體的情況呢，會容易感到燥熱嗎？還是容易流汗呢？"],
    # ["都不會", "了解，您的消化狀況如何？會容易脹氣？還是會肚子痛或是胃痛等等"],
    # ["有時候會脹氣，其他沒有什麼狀況", "了解了，那您最近的排便有遇到什麼問題嗎？是否有腹瀉或是便秘的情況"],
    # ["都不會", "知道了，最近的飲食狀況如何？三餐是否正常？通常吃什麼樣的食物，可以稍微描述一下"],
    # ["三餐蠻正常的，但比較容易吃油膩食物", "好的了解，接下來告訴我您口腔的情況，是否會口苦、口乾、口臭或是容易口渴？嘴吧是否容易破皮？"],
    # ["蠻常會口臭，也容易嘴破", "好的了解，那您尿液的情況如何呢，顏色或是是否有出現泡沫的情況？"],
    # ["尿液顏色淡黃，沒有泡沫", "了解您的情況了，關於身體的整體情況已蒐集完成，接下來會針對睡眠問題做詢問，稍微描述一下您睡眠的情況，是否有早醒、睡不著或是淺眠的情況，也可告知您的平均的睡眠時長"],
    # ["容易早醒，非常容易睡不著，也非常淺眠，容易被外在干擾睡眠，平均時間大約5小時甚至更少", "了解，是否有睡眠前使用手機的習慣呢？"],
    # ["有時候會，但不是每次，大多時間是坐在電腦前寫程式", "知道了，那您經常熬夜嗎？如果有的話請告知您大概都會熬夜到幾點"],
    # ["蠻常熬夜的，通常會到兩三點", "了解了，是否經常感覺壓力很大？您覺得是什麼樣的事情造成您的壓力"],
    # ["大多是課業與工作，要兼顧，又事情太多", "大致上了解您的情況了，接下來會根據您的情況做診斷，您的情況是最近睡不太好，經常感覺壓力大，大多是課業與工作，常常熬夜到兩三點。我的月經週期正常，但疼痛感加劇。我平時手腳容易感到冰冷，身體不會燥熱或流汗，有時會脹氣但其他消化狀況正常。排便沒有問題，三餐較為正常，但容易吃油膩食物。我經常口臭且嘴巴容易破，尿液顏色淡黃且沒有泡沫。睡眠方面，我容易早醒，入睡困難且淺眠，平均睡眠時間約5小時甚至更少。雖然偶爾在睡前會使用手機，但更多時間是坐在電腦前寫程式。"],
    [None, "您好，我是AI中醫問診系統L AI，請問今天有需要諮詢嗎？"],
]


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

    # Update chat_history with the new user input and AI response
    ai_response = state['output']
    history.append([message, ai_response])

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
