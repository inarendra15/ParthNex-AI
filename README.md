ParthNex AI

ParthNex AI is an AI-powered recruitment and Applicant Tracking System(ATS) backend combining resume processing, semantic search, skillmatching, candidate ranking, recruitment workflow management,interviews, offers, dashboards, and activity/audit logging.

The current phase contains the integrated and end-to-end tested backendand AI engine. A frontend can be built on top of the existing FastAPIAPIs.

Core Features

Authentication and Users

Candidate registration and login

JWT-based authentication

Authenticated /users/me

Role-aware access control

Public registration restricted to the candidate role

Recruiter-protected recruitment operations

Resume Management

PDF, DOC, and DOCX uploads

Unique stored filenames

PostgreSQL resume metadata

Candidate-specific resume listing

Resume download and deletion

Automatic FAISS indexing after upload

AI Resume Processing

Resume parsing and text preprocessing

Embedding generation

Semantic job/resume matching

Skill extraction and matching

Matched and missing skill analysis

Resume section analysis

Experience analysis

Resume quality analysis

Candidate Ranking

The ranking pipeline combines semantic similarity, skills, experience,resume quality, and section completeness.

The tested ranking weights were:

Signal         Weight

Semantic         0.35Skills           0.30Experience       0.15Quality          0.10Sections         0.10

Ranking output includes candidate rank, semantic score, skill score,overall score, ranking score, recommendation, matched skills, missingskills, and shortlist decision.

FAISS Vector Search

Persistent FAISS resume index

Resume-ID mapping

Top-K semantic retrieval

Index loading/saving

Candidate deduplication in the ranking flow

Recruitment Management

Jobs CRUD

Applications and application status management

AI score persistence

Shortlist persistence

Interview scheduling, rounds, status, feedback, rating, andrecommendation

Offer creation and lifecycle management

Dashboard endpoints

Full activity/audit timeline

Recruitment Workflow

Candidate Registration
        ↓
Resume Upload
        ↓
Resume Parsing + FAISS Indexing
        ↓
Job Application
        ↓
AI Matching & Ranking
        ↓
Applied → Screened / Shortlisted
        ↓
Interview
        ↓
Interview Feedback
        ↓
Selected / Rejected
        ↓
Offer Created
        ↓
Draft → Sent → Accepted

AI reranking is restricted to early recruitment stages. Recruiter/finaldecisions such as interview, selected, and rejected are protectedfrom being overwritten by subsequent AI reranking.

Technology Stack

Backend

Python

FastAPI

SQLAlchemy

PostgreSQL

Pydantic

JWT authentication

AI / Machine Learning

Text embeddings

FAISS

Resume parsing and preprocessing

Semantic similarity

Skill extraction and matching

Custom candidate ranking

Section, experience, and quality analysis

Development

Git / GitHub

Python virtual environment

FastAPI OpenAPI / Swagger UI

Project Structure

ParthNex-AI/
├── ai_engine/
│   ├── analyzer/
│   ├── builders/
│   ├── data/
│   ├── embeddings/
│   ├── extractors/
│   ├── matcher/
│   ├── parsers/
│   ├── preprocess/
│   ├── ranking/
│   ├── recommendation/
│   ├── schemas/
│   ├── scorer/
│   ├── utils/
│   └── vectorstore/
├── server/
│   └── app/
│       ├── api/v1/
│       ├── config/
│       ├── core/
│       ├── database/
│       ├── dependencies/
│       ├── middleware/
│       ├── models/
│       ├── repositories/
│       ├── schemas/
│       ├── services/
│       └── utils/
└── README.md

Database

Verified PostgreSQL tables:

users
resumes
jobs
applications
interviews
offers
activities

Important verified relationships include: -resumes.user_id → users.id - applications.candidate_id → users.id -applications.job_id → jobs.id -applications.resume_id → resumes.id -interviews.application_id → applications.id -interviews.candidate_id → users.id - interviews.job_id → jobs.id -offers.application_id → applications.id -offers.candidate_id → users.id - offers.job_id → jobs.id

Verified uniqueness rules include: - Unique user email - Unique resumestored filename - Unique (job_id, candidate_id) application - Unique(application_id, round_number) interview - Unique offerapplication_id

Database integrity testing found no orphan applications, interviews,offers, or activities in the tested relationships and no testedparent/candidate/job ownership mismatches.

API Overview

The application currently exposes 42 OpenAPI paths.

Users

POST /users/register
POST /users/login
GET  /users/me

Resumes

POST   /resumes/upload
GET    /resumes/my
GET    /resumes/download/{resume_id}
DELETE /resumes/{resume_id}

Jobs

POST       /jobs/test-match
GET, POST  /jobs
GET        /jobs/{job_id}
PATCH      /jobs/{job_id}
DELETE     /jobs/{job_id}

ATS and Ranking

POST /ats/analyze
POST /ranking/candidates
POST /ranking/jobs/{job_id}

Applications

GET, POST /applications
GET        /applications/job/{job_id}
GET        /applications/candidate/{candidate_id}
GET        /applications/{application_id}
DELETE     /applications/{application_id}
PATCH      /applications/{application_id}/status
PATCH      /applications/{application_id}/scores

Dashboard

GET /dashboard/summary
GET /dashboard/jobs
GET /dashboard/jobs/{job_id}
GET /dashboard/jobs/{job_id}/top-candidates

Interviews

GET, POST /interviews
GET        /interviews/application/{application_id}
GET        /interviews/job/{job_id}
GET        /interviews/{interview_id}
PATCH      /interviews/{interview_id}
DELETE     /interviews/{interview_id}
PATCH      /interviews/{interview_id}/status
PATCH      /interviews/{interview_id}/feedback

Offers

GET, POST /offers
GET        /offers/application/{application_id}
GET        /offers/job/{job_id}
GET        /offers/candidate/{candidate_id}
GET        /offers/{offer_id}
PATCH      /offers/{offer_id}
DELETE     /offers/{offer_id}
PATCH      /offers/{offer_id}/status

Activities

GET /activities
GET /activities/application/{application_id}
GET /activities/job/{job_id}
GET /activities/candidate/{candidate_id}
GET /activities/{activity_id}

System

GET /
GET /health

AI Ranking Pipeline

Job Description
      ↓
Text Cleaning
      ├── Skill Extraction
      ↓
Embedding Generation
      ↓
FAISS Similarity Search
      ↓
Resume Retrieval & Parsing
      ├── Skill Extraction
      ├── Section Analysis
      ├── Experience Analysis
      └── Quality Analysis
      ↓
Candidate Ranker
      ↓
Shortlist Engine
      ↓
Persist AI Scores
      ↓
Activity / Audit Logging

Activity and Audit System

The backend records important recruitment events, including: -Application created - AI scores updated - Application status changed -Interview scheduled - Interview completed - Interview feedback updated -Offer created - Offer sent - Offer accepted

Activities can be retrieved globally and by application, job, orcandidate.

The ranking flow was verified to avoid duplicate activity records whenreranking produces no actual change.

Verified Business Rules

Public registration cannot self-assign recruiter privileges.

Duplicate applications for the same job/candidate are prevented.

Duplicate interview rounds for the same application are prevented.

Offers can only be created for applications that satisfy therequired selected state.

Only one offer can exist per application.

AI ranking may update early-stage recruitment decisions.

AI reranking does not overwrite recruiter/final states such asinterview, selected, or rejected.

Repeated ranking with unchanged data does not create unnecessaryaudit events.

Local Setup

1. Clone and enter the repository

git clone <your-repository-url>
cd ParthNex-AI

2. Create and activate the virtual environment

Windows PowerShell:

python -m venv server/venv
.\server\venv\Scripts\Activate.ps1

3. Install dependencies

Install the dependencies defined by the dependency file used by thisrepository.

4. Configure environment variables

Configure the PostgreSQL connection, JWT/security settings, and othervalues required by server/app/config.

An HF_TOKEN may optionally be configured to avoid unauthenticatedHugging Face Hub warnings and receive higher download rate limits.

5. Run the backend

Because the backend uses app.* imports, start it from server:

cd server
uvicorn app.main:app --reload

Use the FastAPI /docs route for Swagger UI.

Verification Commands

From the project root:

git diff --check
python -m compileall ai_engine server/app
git status

Application import/OpenAPI verification:

cd server
python -c "from app.main import app; print('APP IMPORT SUCCESS'); print('OpenAPI endpoints:', len(app.openapi()['paths']))"

Verified result:

APP IMPORT SUCCESS
OpenAPI endpoints: 42

Final Git verification:

On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean

End-to-End Verification

The following workflow was manually verified:

Authentication                         ✓
Resume retrieval/upload               ✓
Application creation                  ✓
AI matching and ranking               ✓
AI score persistence                  ✓
Activity creation                     ✓
Application status transitions        ✓
Interview scheduling                  ✓
Duplicate interview protection        ✓
Interview completion                  ✓
Interview feedback                    ✓
Candidate selection                   ✓
Offer creation                        ✓
Duplicate offer protection            ✓
Offer sent                            ✓
Offer accepted                        ✓
Final-state reranking protection      ✓
Audit idempotency                     ✓
Database relationship integrity       ✓
FastAPI import/OpenAPI generation      ✓

Current Status

Backend: Completed for the current phase

AI Engine: Integrated

PostgreSQL: Working

FAISS: Working

Authentication: Working

Recruitment Workflow: End-to-end tested

Activity/Audit System: Working

FastAPI/OpenAPI: Verified

OpenAPI Paths: 42

Git Working Tree: Clean

Frontend: Future phase

Future Development

Potential next phases: - Candidate and recruiter frontend - Recruiterdashboard UI - Visual recruitment pipeline - Resume and rankinganalytics - Interview calendar integration - Email notifications - Offerdocument generation - Background resume indexing - Queue-based AIprocessing - Automated test suite and CI/CD - Containerized deployment -Cloud deployment - Production observability and monitoring

Project Goal

ParthNex AI aims to make recruitment workflows more intelligent andstructured by combining traditional ATS functionality with AI-basedresume understanding and candidate ranking while keeping recruiterdecisions authoritative throughout later stages of the hiring process.

License

Add the appropriate project license before public distribution.