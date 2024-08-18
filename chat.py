import chain

def chat_gen(message, history=None, return_buffer=True, state=None):
    if history is None:
        history = []
    if state is None:
        state = {}

    # Update the state with the new input and history
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