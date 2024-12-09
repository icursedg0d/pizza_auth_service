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


def wait_for_db(host, port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            connection = psycopg2.connect(
                host=host,
                port=port,
                user="pizza",
                password="your_password",
                dbname="pizza_auth"
            )
            connection.close()
            return True
        except OperationalError:
            time.sleep(1)
    return False


if __name__ == "__main__":
    if wait_for_db('db', 5432):
        print("База данных готова")
        subprocess.run(["alembic", "revision", "--autogenerate",
                        "-m", "Initial migration"])
        print("Migration created successfully.")
        subprocess.run(["alembic", "upgrade", "head"])
        print("Database upgraded successfully.")

        uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
    else:
        print("База данных не доступна в течение заданного времени")
