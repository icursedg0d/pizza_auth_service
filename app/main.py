from fastapi import FastAPI
from app.routers import auth
import subprocess
import time
import psycopg2
from psycopg2 import OperationalError
import uvicorn

app = FastAPI()


@app.get("/")
async def welcome() -> dict:
    return {"message": "auth-service"}

app.include_router(auth.router)


if __name__ == "__main__":
    # print("База данных готова")
    # subprocess.run(["alembic", "revision", "--autogenerate",
    #                 "-m", "Initial migration"])
    # print("Migration created successfully.")
    # subprocess.run(["alembic", "upgrade", "head"])
    # print("Database upgraded successfully.")

    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
