from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.main import init_db
from src.countries.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n----Server started----\n")
    await init_db()
    yield
    print("\n----Server closed----\n")


app = FastAPI(
    title="HNG Backend task 3",
    description="HNG Backedn task 3 endpoints",
    lifespan=lifespan
)

app.include_router(router, prefix='/countries')