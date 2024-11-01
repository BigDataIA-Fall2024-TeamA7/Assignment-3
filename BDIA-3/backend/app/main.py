from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .middleware.privacy import PrivacyMiddleware
from .routers import documents, qa, search, auth, research_notes, reports
from .services.multimodal_rag_service import MultiModalRAGService
from .services.nemo_service import NeMoMultimodalService
from .services.report_generation_service import ReportService
from .services.validation_service import ValidationService
from .services.vector_store_service import VectorStoreService
from .routers import documents, qa, search, auth, research_notes, reports, validation


# Initialize FastAPI app
app = FastAPI(title="Document Explorer API")

# Initialize middleware
privacy_middleware = PrivacyMiddleware()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add privacy middleware
@app.middleware("http")
async def privacy_middleware_handler(request: Request, call_next):
    """Handle privacy checks for all requests"""
    # Only process POST/PUT requests that might contain sensitive data
    if request.method in ["POST", "PUT"]:
        await privacy_middleware.process_request(request)
    
    response = await call_next(request)
    return response

# Initialize services
nemo_service = NeMoMultimodalService()
report_service = ReportService(nemo_service)
validation_service = ValidationService()
vector_store = VectorStoreService()
multimodal_rag_service = MultiModalRAGService()

# Add services to app state
app.state.nemo_service = nemo_service
app.state.report_service = report_service
app.state.validation_service = validation_service
app.state.vector_store = vector_store
app.state.multimodal_rag_service = multimodal_rag_service
# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(qa.router, prefix="/qa", tags=["Q&A"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(research_notes.router, prefix="/research_notes", tags=["Research Notes"])
app.include_router(validation.router, prefix="/validation", tags=["Validation"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
