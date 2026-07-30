from app.database.base import Base
from app.database.session import engine
from app.api.v1.users import router as user_router

from fastapi import FastAPI
app = FastAPI(
    title="ParthNex AI",
    description="Intelligent Resume Screening & Recruitment Platform",
    version="1.0.0",
)
Base.metadata.create_all(bind=engine)

app.include_router(user_router)

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