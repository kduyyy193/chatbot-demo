from fastapi import APIRouter
from src.models.message import Message
from src.services.chatbot import distilbert_chatbot

router = APIRouter()


@router.post("/chat")
async def chat(message: Message):
    response = distilbert_chatbot(message.text)
    return {"response": response, "input": message.text}
