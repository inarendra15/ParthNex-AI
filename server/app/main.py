from fastapi import FastAPI

from app.database.base import Base
from app.database.session import engine

from app.api.v1.router import api_router

app = FastAPI(
    title="ParthNex AI",
    description="Intelligent Resume Screening & Recruitment Platform",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)

# Register all API routers
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "project": "ParthNex AI",
        "message": "Backend is running successfully 🚀",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ParthNex AI Backend",
    }