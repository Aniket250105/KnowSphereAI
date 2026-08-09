from fastapi import HTTPException, status, Depends
from src.api.dependencies import get_current_user

ROLE_HIERARCHY = {
    "ADMIN": 3,
    "MANAGER": 2,
    "USER": 1
}

def require_role(min_role: str):
    def role_checker(current_user = Depends(get_current_user)):
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
        user_role_level = ROLE_HIERARCHY.get(current_user.role, 0)
        required_role_level = ROLE_HIERARCHY.get(min_role, 0)
        
        if user_role_level < required_role_level:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        
        return current_user
    return role_checker
