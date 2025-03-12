# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from src.core.dialogue_engine import initialization, run

app = FastAPI()

# Update CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=False,  # Must be False if allow_origins is ["*"]
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class Message(BaseModel):
    text: str

@app.get("/init")
async def start():
    global user
    global nlg
    user, nlg, opening= initialization()
    return {"response": opening}

@app.post("/chat")
async def chat(message: Message):
    # Replace this with your chatbot logic
    if user.get_parent_fsm_state() == "task execution":
        response = run(user, nlg, message.text)
        return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)