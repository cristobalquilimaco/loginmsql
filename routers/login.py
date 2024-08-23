from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Dict, Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1  # Duration in minutes
SECRET = "ASJGDJAHSVDajsbjaS1as26552DHFJ6000288ksaBVSJA"

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

users_db: Dict[str, Dict[str, str]] = {}

class User(BaseModel):
    username: str
    email: str
    password: str
    disabled: bool

class u