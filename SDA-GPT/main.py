from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
import openai

app = FastAPI()

openai.api_key = "your-openai-api-key" # Change this with the actual Key

messages = [{"role": "system", "content": "You are a 7th day adventist christian, you never give generic answers, you answer as a 7th day adventist christian always "}]

def CustomChatGPT(question):
    
    # Temporary message for any prompt
    return "OpenAI bill needs to be paid"
    
    # Uncomment the following lines to use the actual OpenAI API again

    # messages.append({"role": "user", "content": question})
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=messages
    # )
    # chatGPT_reply = response["choices"][0]["message"]["content"]
    # messages.append({"role": "assistant", "content": chatGPT_reply})
    # return chatGPT_reply

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html") as f:
        return HTMLResponse(content=f.read())

@app.post("/ask")
async def ask(user_input: str = Form(...)):
    response = CustomChatGPT(user_input)
    return JSONResponse(content={"response": response})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
