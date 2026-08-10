"""
Authentification – JWT + API Key
================================

Gère l'authentification des utilisateurs et des partenaires BRI.

License: CC BY-SA 4.0 – Marc Daghar
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from passlib.context import CryptContext
import secrets
import os

# ---- Configuration ----
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 heures

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# ---- Base de données utilisateurs (temporaire) ----
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("changeme123"),
        "api_key": secrets.token_urlsafe(32),
        "role": "admin"
    },
    "muhtassib_ahmed": {
        "username": "muhtassib_ahmed",
        "hashed_password": pwd_context.hash("inspect123"),
        "api_key": secrets.token_urlsafe(32),
        "role": "muhtassib"
    },
    "bri_china": {
        "username": "bri_china",
        "hashed_password": pwd_context.hash("china_bri_2026"),
        "api_key": "CHN_2026_KEY",
        "role": "partner"
    },
    "bri_russia": {
        "username": "bri_russia",
        "hashed_password": pwd_context.hash("russia_bri_2026"),
        "api_key": "RUS_2026_KEY",
        "role": "partner"
    },
    "bri_turkey": {
        "username": "bri_turkey",
        "hashed_password": pwd_context.hash("turkey_bri_2026"),
        "api_key": "TUR_2026_KEY",
        "role": "partner"
    }
}

# ---- Fonctions d'authentification ----
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe"""
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str) -> Optional[Dict]:
    """Récupère un utilisateur par son nom"""
    return fake_users_db.get(username)

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authentifie un utilisateur"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_api_key(api_key: str) -> bool:
    """Vérifie une clé API"""
    for user in fake_users_db.values():
        if user.get("api_key") == api_key:
            return True
    return False

# ---- Dépendances FastAPI ----
class APIKeyHeader(HTTPBearer):
    async def __call__(self, credentials: HTTPAuthorizationCredentials = Security(security)):
        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme")
        return credentials.credentials

def get_current_user(credentials: str = Security(APIKeyHeader())) -> Dict:
    """Récupère l'utilisateur courant (JWT ou API Key)"""
    # Essayer JWT
    try:
        payload = jwt.decode(credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = get_user(username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        # Essayer comme API Key
        if verify_api_key(credentials):
            # Trouver l'utilisateur correspondant
            for user in fake_users_db.values():
                if user.get("api_key") == credentials:
                    return user
        raise HTTPException(status_code=401, detail="Invalid credentials")

def get_current_admin(user: Dict = Depends(get_current_user)) -> Dict:
    """Vérifie que l'utilisateur est admin"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user

def get_current_muhtassib(user: Dict = Depends(get_current_user)) -> Dict:
    """Vérifie que l'utilisateur est muhtassib ou admin"""
    if user.get("role") not in ["muhtassib", "admin"]:
        raise HTTPException(status_code=403, detail="Muhtassib role required")
    return user

def get_current_partner(user: Dict = Depends(get_current_user)) -> Dict:
    """Vérifie que l'utilisateur est un partenaire BRI"""
    if user.get("role") not in ["partner", "admin"]:
        raise HTTPException(status_code=403, detail="Partner role required")
    return user
