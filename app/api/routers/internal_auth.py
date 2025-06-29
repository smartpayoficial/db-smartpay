from typing import Optional

from fastapi import APIRouter, Header, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel

from app.infra.postgres.models.user import User, UserState
from app.schemas.user import UserCreate

# Dependency to ensure endpoint is only accessible internally


def _internal_only(
    x_internal_request: Optional[str] = Header(None, alias="X-Internal-Request")
):
    if x_internal_request != "true":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Endpoint available only for internal requests",
        )


router = APIRouter(
    include_in_schema=False,  # ocultar en /docs públicas
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -------------------- helpers actualizados -----------------------


def _user_to_response(user: User, include_password: bool = True) -> dict:
    """Build required JSON. include_password=False omits password_hash field."""
    role = user.role
    data = {
        "user_id": str(user.user_id),
        "username": user.username,
        "is_active": user.state == UserState.ACTIVE,
        "role": {"id": str(role.role_id), "name": role.name} if role else None,
    }
    if include_password:
        data["password_hash"] = user.password
    return data


# ---------------------------- endpoints ---------------------------


@router.get("/users/by-username/{username}")
async def get_user_by_username(username: str):
    """Return user info by username or 404."""
    user = await User.filter(username=username).prefetch_related("role").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return _user_to_response(user)


class VerifyBody(BaseModel):
    username: str
    password: str


@router.post("/auth/verify")
async def verify_credentials(body: VerifyBody):
    """Verify username & password. Returns {valid: bool, user: ...}."""
    user = await User.filter(username=body.username).prefetch_related("role").first()

    if not user or not pwd_context.verify(body.password, user.password):
        return {"valid": False, "user": None}

    return {"valid": True, "user": _user_to_response(user)}


# ------------------- Alta interna de usuario ---------------------


@router.post("/users", status_code=201)
async def create_internal_user(new_user: UserCreate):
    """Create user internally: checks uniqueness, hashes password, returns user JSON without password."""
    # Check uniqueness constraints
    exists = await User.filter(username=new_user.username).exists()
    if exists:
        raise HTTPException(status_code=400, detail="Username already exists")
    exists = await User.filter(email=new_user.email).exists()
    if exists:
        raise HTTPException(status_code=400, detail="Email already exists")
    exists = await User.filter(dni=new_user.dni).exists()
    if exists:
        raise HTTPException(status_code=400, detail="DNI already exists")

    # Hash password & save
    hashed_pw = pwd_context.hash(new_user.password)
    user_obj = new_user.dict()
    user_obj["password"] = hashed_pw

    # Create user
    user = await User.create(**user_obj)
    await user.fetch_related("role")

    return _user_to_response(user, include_password=False)
