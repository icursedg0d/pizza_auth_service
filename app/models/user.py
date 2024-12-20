from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    address = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
