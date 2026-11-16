"""Applications Entry Point Run: uvicorn app.main:app --reload"""

from fastapi import FastAPI
from app.routers import basics, params, crud, bodies

app = FastAPI(title="FastAPI Handbook", version="1.0.0")


app.include_router(basics.router)
app.include_router(params.router)

app.include_router(bodies.router)
app.include_router(crud.router)