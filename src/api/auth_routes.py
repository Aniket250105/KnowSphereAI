from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from src.auth.auth_service import register_user, authenticate_user
from src.auth.jwt_handler import decode_token, create_access_token
from src.api.dependencies import get_db

router = APIRouter()

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, request)
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role
        }
    }

@router.post("/login")
async def login(request: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    tokens = await authenticate_user(db, request)
    
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3600
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=86400 * 7
    )
    
    payload = decode_token(tokens["access_token"])
    return {
        "user": {
            "id": payload.get("user_id"),
            "email": payload.get("email"),
            "username": payload.get("username"),
            "role": payload.get("role")
        }
    }

@router.get("/me")
async def get_current_user(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = decode_token(access_token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")
        
    return {
        "user": {
            "id": payload.get("user_id"),
            "email": payload.get("email"),
            "username": payload.get("username"),
            "role": payload.get("role")
        }
    }

@router.post("/refresh")
async def refresh(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
        
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    new_payload = {
        "user_id": payload.get("user_id"),
        "username": payload.get("username"),
        "email": payload.get("email"),
        "role": payload.get("role"),
        "organization_id": payload.get("organization_id")
    }
    
    new_access_token = create_access_token(data=new_payload)
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3600
    )
    return {"message": "Token refreshed"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}
