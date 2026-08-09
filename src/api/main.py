from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router as main_router
from src.api.admin_routes import admin_router
from src.api.auth_routes import router as auth_router
from src.api.evaluation_routes import evaluation_router
from src.api.agent_routes import router as agent_router
from fastapi.staticfiles import StaticFiles
from src.ui.routes import router as ui_router
import os

app = FastAPI(
    title="KnowSphere AI Backend",
    description="API for Document Ingestion, Retrieval, and RAG",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(main_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/admin")
app.include_router(evaluation_router, prefix="/api/v1/admin/evaluation")
app.include_router(agent_router, prefix="/api/v1/agent")

# Mount Static Files
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount UI Routes
app.include_router(ui_router)

@app.on_event("shutdown")
async def shutdown_event():
    pass
