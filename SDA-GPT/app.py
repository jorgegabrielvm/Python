from flask import Flask, render_template, request
import openai

app = Flask(__name__)

openai.api_key = "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"

messages = [{"role": "system", "content": "You are a 7th day adventist christian, you never give generic answers, you answer as7th day adventist christian always "}]

def CustomChatGPT(question):
    messages.append({"role": "user", "content": question})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    chatGPT_reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": chatGPT_reply})
    return chatGPT_reply

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['user_input']
    response = CustomChatGPT(user_input)
    return response
