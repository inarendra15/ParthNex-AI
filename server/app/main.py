from fastapi import FastAPI

from app.database.base import Base
from app.database.session import engine

from app.api.v1.router import api_router

from app.api.v1.ats import router as ats_router
from app.api.v1.ranking import router as ranking_router

from app.api.v1.applications import router as applications_router
from app.api.v1.dashboard import router as dashboard_router

from app.api.v1.interviews import router as interviews_router
from app.api.v1 import offers


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

app.include_router(ats_router)
app.include_router(ranking_router)
app.include_router(applications_router)
app.include_router(dashboard_router)
app.include_router(interviews_router)
app.include_router(offers.router)