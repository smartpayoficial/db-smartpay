from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.infra.postgres.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # This is a placeholder. In a real application, you would decode the JWT token
    # and validate it. For now, we'll just return a dummy user.
    user = await User.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
