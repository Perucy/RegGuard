from fastapi import FastAPI
from regguard.schemas.chat import ChatRequest, ChatResponse
from regguard.services.llm_service import get_chat_response
from regguard.agents.simple_agent import ofac_sdn_agent


app = FastAPI(
    title="RegGuard API",
    description="Supply chain compliance monitoring",
    version="0.1.0"
)

@app.post("/api/compliance/check-sanctions")
async def api_check_sanctions(company_name: str, fuzzy: bool = True):
    """
    Check if a company or person is on OFAC sanctions list.
    
    Args:
        company_name: Name to check (query parameter)
        fuzzy: Enable fuzzy matching for typos (query parameter)
        
    Returns:
        Sanctions check results from AI agent
    """
    # Pass parameters to agent
    result = await ofac_sdn_agent(company_name, fuzzy)
    
    return {
        "company_name": company_name,
        "fuzzy_enabled": fuzzy,
        "result": result
    }

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
