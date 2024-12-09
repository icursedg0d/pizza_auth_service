from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, insert

from app.models.user import User
from app.schemas import CreateUser
from app.backend.db_depends import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["auth"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

SECRET_KEY = "1f1e92bade502438c1789b443955912dfbc19a1cfde28fdf4612acf13a194f87"
ALGORITHM = "HS256"


async def create_access_token(
    first_name: str,
    last_name: str,
    user_id: int,
    is_admin: bool,
    expires_delta: timedelta,
):
    encode = {
        "first_name": first_name,
        "last_name": last_name,
        "id": user_id,
        "is_admin": is_admin,
    }

    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        first_name: str = payload.get("first_name")
        last_name: str = payload.get("last_name")
        is_admin: bool = payload.get("is_admin")
        expire = payload.get("exp")
        if first_name is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user",
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied",
            )
        if datetime.now() > datetime.fromtimestamp(expire):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Token expired!"
            )

        return {
            "id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "is_admin": is_admin,
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    db: Annotated[AsyncSession, Depends(get_db)], create_user: CreateUser
):
    await db.execute(
        insert(User).values(
            first_name=create_user.first_name,
            last_name=create_user.last_name,
            email=create_user.email,
            hashed_password=bcrypt_context.hash(create_user.password),
            is_admin=create_user.email == "admin"
        )
    )
    await db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


async def authenticate_user(
    db: Annotated[AsyncSession, Depends(get_db)], email: str, password: str
):
    user = await db.scalar(select(User).where(User.email == email))
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/token")
async def login(
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = await authenticate_user(db, form_data.username, form_data.password)

    token = await create_access_token(
        first_name=user.first_name,
        last_name=user.last_name,
        user_id=user.id,
        is_admin=user.is_admin,
        expires_delta=timedelta(minutes=60),
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/read_current_user")
async def read_current_user(user: dict = Depends(get_current_user)):
    return {"User": user}
