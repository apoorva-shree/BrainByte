"""
Authentication utilities for JWT token management
Supports NGO and Donor user roles
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, ExpiredSignatureError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY must be set in environment variables")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))  # default 24h

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def create_user_token(user_id: str, email: str, role: str) -> str:
    """Create token for authenticated user"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        data={"sub": user_id, "email": email, "role": role},
        expires_delta=access_token_expires
    )

# Dependency for FastAPI routes
def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """Extract current user from JWT"""
    payload = decode_access_token(token)
    return payload

def ngo_only(current_user: Dict = Depends(get_current_user)):
    """Restrict access to NGO role"""
    if current_user.get("role") != "NGO":
        raise HTTPException(status_code=403, detail="NGO access required")
    return current_user

def donor_only(current_user: Dict = Depends(get_current_user)):
    """Restrict access to Donor role"""
    if current_user.get("role") != "Donor":
        raise HTTPException(status_code=403, detail="Donor access required")
    return current_user