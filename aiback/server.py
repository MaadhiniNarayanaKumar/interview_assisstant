from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model.Interaction import Interaction
from chat.interact import communicate
from func import libs
app = FastAPI()

chat=communicate()

origins = [
    "http://localhost:4200",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    print('in root1')
    return {"message": "Hello World"}

@app.post("/self_intro/", tags=['Interact'])
def self_intro(interaction: Interaction):
    print('in root2',interaction.query)
    model_reply=chat.self_intro(interaction.query)
    return {"message": model_reply}

@app.post("/interact/", tags=['Interact'])
def interact(interaction: Interaction):
    print('in root2',interaction.query)
    model_reply=chat.classify(interaction.query)
    model_reply=libs.str_json(model_reply)
    print('classified as:::',model_reply)
    if model_reply.get('classification') == 'chat':
        model_reply2=chat.chat(interaction.query)
        model_reply2=libs.str_json(model_reply2)
        print('chat as:::',model_reply2)
        if model_reply2.get('classification') == 'not ready':
            model_reply3=chat.converse(interaction.query)
            print('converse as:::',model_reply3)
            return {"message": model_reply3}
        return {"message": model_reply2}
    return {"message": model_reply}
    