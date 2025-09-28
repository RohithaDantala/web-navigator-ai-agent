# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import asyncio
import sys
import logging
import os
from contextlib import asynccontextmanager

# Import the enhanced navigator with LLM integration
from agents.enhanced_web_navigator import WebNavigatorAgent

# Configure clean logging for the API
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Suppress unnecessary logs
logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Fix for Windows
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Global navigator instance
navigator_agent = None

# Request/Response models
class NavigationOptions(BaseModel):
    headless: bool = True
    verbose_chrome: bool = False
    timeout: int = 30

class NavigationRequest(BaseModel):
    instruction: str
    session_id: Optional[str] = None
    options: Optional[NavigationOptions] = NavigationOptions()

class NavigationResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    message: str
    execution_time: float
    content_type: Optional[str] = "general"
    site: Optional[str] = "unknown"
    session_id: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global navigator_agent
    try:
        logger.info("🚀 Initializing Enhanced Web Navigator Agent with LLM integration...")
        navigator_agent = WebNavigatorAgent()
        
        # Initialize with default settings (headless=True for production)
        success = await navigator_agent.initialize(
            headless=True,  # Change to False for debugging
            verbose_chrome=False  # Set to True for Chrome debugging
        )
        
        if success:
            logger.info("✅ Enhanced Web Navigator Agent ready with Llama3 LLM")
            logger.info("🌐 Supported sites: Amazon, GitHub, LinkedIn, Indeed, Stack Overflow, YouTube")
        else:
            logger.error("❌ Failed to initialize Enhanced Web Navigator Agent")
            navigator_agent = None
    except Exception as e:
        logger.error(f"❌ Navigator initialization failed: {e}")
        navigator_agent = None
    
    yield
    
    # Shutdown
    if navigator_agent:
        logger.info("🔄 Shutting down Enhanced Web Navigator Agent...")
        await navigator_agent.cleanup()
        logger.info("✅ Cleanup completed")

# Create FastAPI app
app = FastAPI(
    title="Enhanced Universal Web Navigator",
    version="3.0.0",
    description="AI-powered universal web automation with LLM integration and smart content detection",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/navigate", response_model=NavigationResponse)
async def navigate_web(request: NavigationRequest):
    """
    Execute universal web navigation task with LLM-powered intelligence
    Supports: Amazon, GitHub, LinkedIn, Indeed, Stack Overflow, YouTube, and any website
    Features: Smart content type detection, dynamic action text, LLM-enhanced parsing
    """
    logger.info(f"🔍 New LLM-powered request: {request.instruction}")
    
    try:
        if not navigator_agent:
            logger.error("⚠️ Navigator not available")
            return NavigationResponse(
                success=False,
                data=[],
                message="Navigator service unavailable. Please check server logs and ensure Ollama is running.",
                execution_time=0.0,
                session_id=request.session_id
            )
        
        # Execute the navigation task with LLM integration
        result = await navigator_agent.execute_task(
            instruction=request.instruction,
            options=request.options.dict() if request.options else None
        )
        
        # Log result summary with content type
        data_count = len(result.get("data", []))
        exec_time = result.get("execution_time", 0)
        content_type = result.get("content_type", "general")
        site = result.get("site", "unknown")
        
        if result.get("success"):
            logger.info(f"✅ Task completed: {data_count} {content_type} found on {site} in {exec_time:.2f}s")
        else:
            logger.error(f"❌ Task failed after {exec_time:.2f}s")
        
        return NavigationResponse(
            success=result.get("success", False),
            data=result.get("data", []),
            message=result.get("message", "Task completed"),
            execution_time=exec_time,
            content_type=content_type,
            site=site,
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"❌ Navigation error: {str(e)}")
        return NavigationResponse(
            success=False,
            data=[],
            message=f"Internal error: {str(e)}",
            execution_time=0.0,
            session_id=request.session_id
        )

@app.get("/health")
async def health_check():
    """Health check endpoint with LLM status"""
    return {
        "status": "healthy",
        "service": "Enhanced Universal Web Navigator",
        "version": "3.0.0",
        "navigator_ready": navigator_agent is not None,
        "features": [
            "LLM-powered instruction parsing",
            "Smart content type detection", 
            "Dynamic action text generation",
            "Multi-site support",
            "YouTube integration"
        ],
        "llm_model": "llama3 (Ollama)",
        "requirements": [
            "Ollama server running on localhost:11434",
            "llama3 model downloaded"
        ]
    }

@app.get("/")
async def root():
    """Root endpoint with enhanced features info"""
    return {
        "message": "Enhanced Universal Web Navigator API v3.0 with LLM Integration",
        "documentation": "/docs",
        "health": "/health",
        "new_features": [
            "🧠 LLM-powered instruction understanding",
            "🎯 Smart content type detection (products, jobs, videos, etc.)",
            "🔗 Dynamic action text (View Product, View Job, Watch Video, etc.)",
            "🎬 YouTube video search support",
            "📚 Enhanced result categorization"
        ],
        "supported_sites": [
            "Amazon (products search)",
            "GitHub (repositories)",
            "LinkedIn (jobs - limited without login)",
            "Indeed (job search)",
            "Stack Overflow (questions)",
            "YouTube (videos)",
            "Any website (universal fallback)"
        ],
        "example_commands": [
            "search for Python jobs on LinkedIn",
            "find gaming laptops on Amazon under $1500",
            "search for React repositories on GitHub",
            "find JavaScript questions on Stack Overflow",
            "search for React tutorials on YouTube"
        ],
        "setup_requirements": [
            "Install Ollama: https://ollama.ai/",
            "Download Llama3: ollama pull llama3",
            "Start Ollama server: ollama serve"
        ]
    }

@app.post("/test-navigation")
async def test_navigation():
    """Enhanced test endpoint with different content types"""
    test_commands = [
        "find Python repositories on GitHub",
        "search for gaming laptops on Amazon",
        "Python jobs on LinkedIn",
        "JavaScript questions on Stack Overflow",
        "React tutorials on YouTube"
    ]
    
    results = {}
    
    for command in test_commands:
        try:
            logger.info(f"🧪 Testing: {command}")
            result = await navigate_web(NavigationRequest(instruction=command))
            results[command] = {
                "success": result.success,
                "count": len(result.data),
                "time": result.execution_time,
                "content_type": result.content_type,
                "site": result.site
            }
        except Exception as e:
            results[command] = {"error": str(e)}
    
    return {"test_results": results}

@app.get("/llm-status")
async def llm_status():
    """Check LLM service status"""
    try:
        if navigator_agent and navigator_agent.navigator.llm_service:
            # Test LLM connection
            test_response = await navigator_agent.navigator.llm_service.generate_response(
                "You are a helpful assistant.", 
                "Say 'LLM connection successful' if you can read this."
            )
            
            return {
                "status": "connected" if test_response else "disconnected",
                "model": "llama3",
                "service": "Ollama",
                "endpoint": "http://localhost:11434",
                "test_response": test_response[:100] if test_response else None
            }
        else:
            return {
                "status": "unavailable",
                "message": "Navigator not initialized or LLM service not available"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "troubleshooting": [
                "Ensure Ollama is installed and running",
                "Check if llama3 model is downloaded: ollama pull llama3",
                "Verify Ollama server is running: ollama serve"
            ]
        }

# Custom error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return {"error": exc.detail, "status_code": exc.status_code}

if __name__ == "__main__":
    print("🚀 Starting Enhanced Universal Web Navigator API v3.0")
    print("🧠 Features: LLM Integration, Smart Content Detection, YouTube Support")
    print("📖 Visit http://localhost:8000/docs for API documentation")
    print("🧪 Visit http://localhost:8000/test-navigation to run tests")
    print("🔍 Visit http://localhost:8000/llm-status to check LLM connection")
    print("")
    print("📋 Requirements:")
    print("   • Ollama server running: ollama serve")
    print("   • Llama3 model: ollama pull llama3")
    print("   • Chrome browser installed")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False,  # Set to True for development
        log_level="info"
    )