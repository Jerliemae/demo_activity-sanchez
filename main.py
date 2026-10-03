import os
import asyncio
import csv
from io import StringIO
from fastapi import FastAPI
from fastapi.responses import Response
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        import asyncpg
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        app.state.pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=10,
            statement_cache_size=0
        )
    else:
        app.state.pool = None
    
    yield
    
    if hasattr(app.state, "pool") and app.state.pool:
        await app.state.pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/export/users/csv")
async def export_users_csv():
    rows = [
        {
            "user_id": 1,
            "first_name": "John",
            "middle_name": "Doe",
            "last_name": "Smith"
        },
        {
            "user_id": 2,
            "first_name": "Jane",
            "middle_name": "",
            "last_name": "Doe"
        }
    ]
    
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["user_id", "first_name", "middle_name", "last_name"])
    
    for row in rows:
        writer.writerow([
            row["user_id"],
            row["first_name"],
            row["middle_name"] or "",
            row["last_name"]
        ])
    
    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"}
    )

@app.get("/")
async def root():
    return {"message": "API is running ✅ Use /export/users/csv to download"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
