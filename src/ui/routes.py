from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.api.dependencies import get_current_user
from src.database.models import UserModel
import os

router = APIRouter()

# Setup templates directory
templates = Jinja2Templates(directory="templates")

async def get_optional_user(request: Request):
    try:
        return await get_current_user(request, next(get_db()))
    except:
        return None

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Try to extract cookie for auth check
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/dashboard")
    return RedirectResponse(url="/login")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"active_page": "dashboard"})

@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse(request=request, name="chat.html", context={"active_page": "chat"})

@router.get("/documents", response_class=HTMLResponse)
async def documents_page(request: Request):
    return templates.TemplateResponse(request=request, name="documents.html", context={"active_page": "documents"})

@router.get("/agents", response_class=HTMLResponse)
async def agents_page(request: Request):
    return templates.TemplateResponse(request=request, name="agents.html", context={"active_page": "agents"})

@router.get("/evaluation", response_class=HTMLResponse)
async def evaluation_page(request: Request):
    return templates.TemplateResponse(request=request, name="evaluation.html", context={"active_page": "evaluation"})

@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    return templates.TemplateResponse(request=request, name="history.html", context={"active_page": "history"})

@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    return templates.TemplateResponse(request=request, name="analytics.html", context={"active_page": "analytics"})

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse(request=request, name="settings.html", context={"active_page": "settings"})

@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse(request=request, name="admin.html", context={"active_page": "admin"})
