from fastapi import FastAPI

app = FastAPI(
    title="ParthNex AI",
    description="Intelligent Resume Screening & Recruitment Platform",
    version="1.0.0",
)


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