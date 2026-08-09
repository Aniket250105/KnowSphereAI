from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import UserModel
from src.database.repository import DatabaseRepository
from src.auth.schemas import RegisterRequest, LoginRequest
from src.auth.password_manager import hash_password, verify_password
from src.auth.jwt_handler import create_access_token, create_refresh_token
from fastapi import HTTPException, status

async def register_user(db: AsyncSession, request: RegisterRequest) -> UserModel:
    repo = DatabaseRepository(db)
    # Check if user exists
    existing_user = await repo.get_user(email=request.email, username=request.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    # Hash password
    hashed_password = hash_password(request.password)

    # Simplified org logic for phase 7b
    # Assuming organization 1 is Default. For a real app, query it.
    
    new_user = await repo.create_user(
        username=request.username,
        email=request.email,
        password_hash=hashed_password,
        organization_id=1
    )

    return new_user

async def authenticate_user(db: AsyncSession, request: LoginRequest):
    repo = DatabaseRepository(db)
    user = await repo.get_user(email=request.email)
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "organization_id": user.organization_id
    }
    
    access_token = create_access_token(data=payload)
    refresh_token = create_refresh_token(data=payload)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

