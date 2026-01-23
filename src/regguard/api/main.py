from fastapi import FastAPI
from regguard.schemas.chat import ChatRequest, ChatResponse
from regguard.services.llm_service import get_chat_response


app = FastAPI(
    title="RegGuard API",
    description="Supply chain compliance monitoring",
    version="0.1.0"
)

@app.post("/api/chat", response_model=ChatResponse)
async def llm_endpoint(request: ChatRequest):
    response = await get_chat_response(request.message)
    return ChatResponse(response=response)

@app.get("/")
async def root():
    return {"message": "Welcome to RegGuard"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
