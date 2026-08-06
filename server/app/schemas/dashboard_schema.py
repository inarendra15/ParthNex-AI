from pydantic import BaseModel


# ======================================================
# JOB METRICS
# ======================================================

class JobMetrics(BaseModel):
    total: int
    open: int
    closed: int


# ======================================================
# CANDIDATE METRICS
# ======================================================

class CandidateMetrics(BaseModel):
    total: int


# ======================================================
# RESUME METRICS
# ======================================================

class ResumeMetrics(BaseModel):
    total: int


# ======================================================
# APPLICATION METRICS
# ======================================================

class ApplicationMetrics(BaseModel):
    total: int
    ai_shortlisted: int


# ======================================================
# RECRUITMENT PIPELINE
# ======================================================

class PipelineMetrics(BaseModel):
    applied: int
    screened: int
    shortlisted: int
    interview: int
    selected: int
    rejected: int


# ======================================================
# AI SCORE METRICS
# ======================================================

class AverageScoreMetrics(BaseModel):
    ranking: float
    semantic: float
    skills: float


# ======================================================
# CONVERSION METRICS
# ======================================================

class ConversionRateMetrics(BaseModel):
    ai_shortlist_rate: float
    selection_rate: float


# ======================================================
# DASHBOARD SUMMARY RESPONSE
# ======================================================

class DashboardSummaryResponse(BaseModel):
    jobs: JobMetrics
    candidates: CandidateMetrics
    resumes: ResumeMetrics
    applications: ApplicationMetrics
    pipeline: PipelineMetrics
    average_scores: AverageScoreMetrics
    conversion_rates: ConversionRateMetrics

# ======================================================
# JOB INFORMATION
# ======================================================

class DashboardJobInfo(BaseModel):
    id: int
    title: str
    company: str
    location: str | None = None
    employment_type: str | None = None
    status: str


# ======================================================
# PER-JOB CONVERSION METRICS
# ======================================================

class JobConversionRateMetrics(BaseModel):
    ai_shortlist_rate: float
    interview_rate: float
    selection_rate: float
    rejection_rate: float


# ======================================================
# PER-JOB ANALYTICS RESPONSE
# ======================================================

class JobAnalyticsResponse(BaseModel):
    job: DashboardJobInfo
    applications: ApplicationMetrics
    pipeline: PipelineMetrics
    average_scores: AverageScoreMetrics
    conversion_rates: JobConversionRateMetrics

# ======================================================
# TOP CANDIDATE
# ======================================================

class TopCandidateResponse(BaseModel):
    rank: int

    candidate_id: int
    candidate_name: str
    email: str

    resume_id: int
    filename: str

    ranking_score: float | None = None
    semantic_score: float | None = None
    skill_score: float | None = None

    ai_shortlisted: bool
    status: str


# ======================================================
# TOP CANDIDATES RESPONSE
# ======================================================

class TopCandidatesResponse(BaseModel):
    job_id: int
    job_title: str
    total_returned: int

    candidates: list[TopCandidateResponse]

# ======================================================
# JOB OVERVIEW ITEM
# ======================================================

class JobOverviewResponse(BaseModel):
    job_id: int
    title: str
    company: str
    status: str

    total_applications: int
    ai_shortlisted: int

    interview: int
    selected: int
    rejected: int

    average_ranking_score: float


# ======================================================
# JOBS OVERVIEW RESPONSE
# ======================================================

class JobsOverviewResponse(BaseModel):
    jobs: list[JobOverviewResponse]