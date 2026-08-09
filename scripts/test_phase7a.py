import httpx
import sqlite3
import pytest
from src.core import config
from src.database.database import SessionLocal
from src.database.models import UserModel

API_BASE_URL = "http://localhost:8000/api/v1"
ADMIN_URL = "http://localhost:8000/admin"

def test_auth_and_rbac():
    # 1. Test Registration
    test_user = {
        "username": "testuser_phase7a",
        "email": "testuser_phase7a@example.com",
        "password": "securepassword123"
    }
    
    # Clean up previous runs
    db = SessionLocal()
    db.query(UserModel).filter(UserModel.username == test_user["username"]).delete()
    db.commit()
    db.close()

    try:
        reg_response = httpx.post(f"{API_BASE_URL}/auth/register", json=test_user, timeout=10.0)
        assert reg_response.status_code == 201, f"Expected 201 Created, got {reg_response.status_code}"
        print("✅ Registration successful")
    except httpx.ConnectError:
        print("❌ Could not connect to the API. Is it running?")
        return

    # 2. Test Login
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    login_response = httpx.post(f"{API_BASE_URL}/auth/login", json=login_data)
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    access_token = tokens["access_token"]
    print("✅ Login successful")

    # 3. Test Password Security
    db = SessionLocal()
    user = db.query(UserModel).filter(UserModel.email == test_user["email"]).first()
    assert user is not None
    assert user.password_hash != test_user["password"]
    assert user.password_hash.startswith("$2") # bcrypt standard hash starts with $2
    print("✅ Password securely hashed in database")

    # 4. JWT Validation & RBAC (USER Role)
    # The new user gets 'USER' role by default.
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Endpoint needing MANAGER (e.g., /admin/analytics/system)
    sys_metrics_response = httpx.get(f"{ADMIN_URL}/analytics/system", headers=headers)
    assert sys_metrics_response.status_code == 403, f"Expected 403 Forbidden for USER, got {sys_metrics_response.status_code}"
    print("✅ USER denied access to MANAGER endpoint (403 Forbidden)")

    # 5. Invalid JWT
    bad_headers = {"Authorization": "Bearer invalid.token.value"}
    bad_response = httpx.get(f"{ADMIN_URL}/analytics/system", headers=bad_headers)
    assert bad_response.status_code == 401, f"Expected 401 Unauthorized for invalid token, got {bad_response.status_code}"
    print("✅ Invalid token rejected (401 Unauthorized)")

    # 6. Elevate to ADMIN and Test RBAC
    user.role = "ADMIN"
    db.commit()
    db.close()
    
    # Now that we're ADMIN, generate a new token (or re-login)
    admin_login_response = httpx.post(f"{API_BASE_URL}/auth/login", json=login_data)
    admin_tokens = admin_login_response.json()
    admin_headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}

    # Should be able to access MANAGER endpoint
    sys_metrics_response = httpx.get(f"{ADMIN_URL}/analytics/system", headers=admin_headers)
    assert sys_metrics_response.status_code == 200, f"Expected 200 OK for ADMIN, got {sys_metrics_response.status_code}"
    print("✅ ADMIN accessed MANAGER endpoint (200 OK)")

    # Should be able to access ADMIN endpoint
    user_metrics_response = httpx.get(f"{ADMIN_URL}/analytics/users", headers=admin_headers)
    assert user_metrics_response.status_code == 200, f"Expected 200 OK for ADMIN, got {user_metrics_response.status_code}"
    print("✅ ADMIN accessed ADMIN endpoint (200 OK)")
    
    print("\n🎉 Phase 7A Auth & RBAC tests passed successfully!")

if __name__ == "__main__":
    test_auth_and_rbac()
