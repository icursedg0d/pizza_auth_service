from fastapi import FastAPI
from app.routers import auth
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://pizza-auth-service.onrender.com",
    "https://pizza-catalog-service.onrender.com",
    "https://pizza-build.onrender.com/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
