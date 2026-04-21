# Ethos AI

Ethos AI is an intelligent fairness auditing platform that detects, explains, and helps mitigate bias in machine learning systems.

## Features

- CSV dataset ingestion and validation
- Bias analysis across sensitive groups
- Core fairness metrics:
	- Selection Rate
	- Demographic Parity Difference
	- Disparate Impact Ratio
	- False Positive Rate Difference
- AI-generated explanation (`/explain`, Gemini with fallback)
- Rule-based mitigation recommendation engine (`/recommend`)
- Structured report generation and storage (`/report`)
- React dashboard with upload → analyze → explain → recommend → report flow

## Project Structure

```text
backend/
	app/
		config/
		models/
		routes/
		services/
		utils/
	requirements.txt
	Dockerfile

frontend/
	src/
	public/
	package.json
	firebase.json

data/
reports/
```

## API Endpoints

- `GET /health`
- `POST /upload`
- `POST /analyze`
- `POST /explain`
- `POST /recommend`
- `GET /report`

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+

### 1) Backend setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000`.

Optional environment variables:

- `GEMINI_API_KEY` (for Gemini explanation generation)
- `GEMINI_MODEL` (default: `gemini-1.5-flash`)

### 2) Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://127.0.0.1:5173`.

## End-to-End Workflow

1. Upload CSV in `Upload Page`
2. Move to `Dashboard Page`
3. Select target and sensitive columns, run bias analysis
4. View charts, group metrics, and overall bias indicators
5. Get AI explanation and mitigation recommendations
6. Generate and view final report in `Report View`

Generated report JSON files are stored under:

- `reports/generated/`

## Deployment Prep (Phase 10)

### Backend → Google Cloud Run

`backend/Dockerfile` is included and Cloud Run compatible.

Build and deploy example:

```bash
gcloud builds submit --tag gcr.io/<GCP_PROJECT_ID>/ethos-backend ./backend
gcloud run deploy ethos-backend \
	--image gcr.io/<GCP_PROJECT_ID>/ethos-backend \
	--platform managed \
	--region <REGION> \
	--allow-unauthenticated \
	--set-env-vars GEMINI_API_KEY=<YOUR_KEY>
```

### Frontend → Firebase Hosting

`frontend/firebase.json` and `frontend/.firebaserc` are included.

Deploy example:

```bash
cd frontend
npm install
npm run build
npm install -g firebase-tools
firebase login
firebase use <YOUR_FIREBASE_PROJECT_ID>
firebase deploy --only hosting
```

Update `frontend/.firebaserc` default project before deploy.
