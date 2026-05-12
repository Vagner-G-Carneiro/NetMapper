from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from schemas.auth import UserCreate, UserLogin, Token, UserOut
import services.auth_service as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(db, data)


@router.post("/login/api", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    return auth_service.login_user(db, data)

#Recebe HTML form data, útil para testes no Swagger UI
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    data = UserLogin(email=form_data.username, password=form_data.password)
    return auth_service.login_user(db, data)