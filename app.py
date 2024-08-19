from flask import Flask, jsonify, request

app = Flask(__name__)

# 初始化一個變數來儲存輸出句子
output_sentence = "who are u"

# 獲取當前的輸出句子
@app.route('/get_sentence', methods=['GET'])
def get_sentence():
    return jsonify(message=output_sentence)

# 更新當前的輸出句子
@app.route('/update_sentence', methods=['POST'])
def update_sentence():
    global output_sentence
    new_sentence = request.json.get('sentence')
    if new_sentence:
        output_sentence = new_sentence
        return jsonify(message="句子已更新。"), 200
    return jsonify(error="未提供新的句子。"), 400

if __name__ == '__main__':
    app.run(debug=True)