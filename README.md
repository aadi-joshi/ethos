# Ethos AI

Intelligent fairness auditing platform to detect, explain, and mitigate bias in machine learning systems.

## Phase 1 Status
- Project skeleton initialized
- FastAPI backend scaffold with health endpoint
- React frontend initialized with landing page

## Local Run

### Backend (FastAPI)
1. Create/activate a Python environment.
2. Install dependencies:
	```bash
	pip install -r backend/requirements.txt
	```
3. Run API:
	```bash
	cd backend
	uvicorn app.main:app --reload
	```
4. Check health endpoint:
	```bash
	curl http://127.0.0.1:8000/health
	```

### Frontend (React + Vite)
1. Install dependencies:
	```bash
	cd frontend
	npm install
	```
2. Run development server:
	```bash
	npm run dev
	```
