# Ethos AI

> **Google Solution Challenge 2026 - Unbiased AI Decision Track**
>
> India's first accessible LLM bias auditing platform. Counterfactual probing for caste, gender, religion, and regional bias in AI systems making decisions about real people's lives.

---

## The Problem

AI systems in India make high-stakes decisions about hiring, lending, education, and healthcare. Existing fairness tools (IBM AIF360, Microsoft Fairlearn, Google What-If Tool) have three critical gaps:

1. **They don't probe LLMs** - they require model internals, not just natural language outputs
2. **They don't understand India** - no support for caste, religion-based, or regional bias dimensions
3. **They're not accessible** - require ML expertise, inaccessible to affected citizens

Ethos AI fills all three gaps.

---

## Three-Pillar Architecture

### 1. LLM Bias Probe (Primary Differentiator)

Counterfactual probing: send identical prompts to any AI, changing only the demographic signal (applicant name). Any statistically significant difference in outputs is attributable to that signal - bias.

Methodology: Bertrand & Mullainathan (2004) - "Are Emily and Greg More Employable than Lakisha and Jamal?"

**India-specific bias dimensions:**
- **Caste**: Upper-caste surnames (Sharma, Iyer, Kulkarni, Thakur) vs SC/ST surnames (Paswan, Baudh, Munda, Murmu)
- **Religion**: Hindu vs Muslim vs Sikh vs Christian names
- **Gender**: Male vs female first names
- **Region**: North Urban vs Northeast India demographic signals

**Domains:** Hiring, bank lending, university admissions, healthcare triage

**Outputs per probe run:**
- Acceptance rate differential (percentage point gap)
- Disparate Impact Ratio (DIR) - EEOC 4/5 rule threshold: 0.80
- Fisher's Exact Test p-value for statistical significance
- AI narrative analysis via Gemini
- Remediation plan
- India compliance assessment (DPDP Act 2023, Articles 15 & 16)

**Demo mode**: No API key required. Pre-generated responses show 70% vs 35% shortlist rate for caste bias in hiring.

### 2. ML Model Fairness Audit

Upload any CSV dataset. Get 6 fairness metrics:

| Metric | Description |
|--------|-------------|
| Demographic Parity Difference | Selection rate gap between groups |
| Disparate Impact Ratio | min/max selection rate ratio (EEOC threshold: 0.80) |
| FPR Difference | False positive rate gap |
| Equal Opportunity Difference | True positive rate gap |
| Average Odds Difference | Mean of FPR diff and TPR diff |
| Theil Index | Entropy-based inequality measure |

**Mitigation**: Download a reweighed dataset (Kamiran & Calders, 2012) with a `sample_weight` column.

### 3. Citizen Bias Map

Anonymous report submission (web + mobile). Aggregated data shows an India heatmap of algorithmic discrimination reports. Every submission receives a Gemini preliminary assessment and India grievance portal links.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI (Python) |
| LLM Integration | Google Gemini API |
| Database | Google Cloud Firestore (in-memory fallback) |
| Frontend | React 18 + Vite + Recharts |
| Mobile | Flutter 3 (Android/iOS) |
| Backend Hosting | Google Cloud Run |
| Frontend Hosting | Firebase Hosting |
| Statistics | scipy, pandas, scikit-learn |

---

## Project Structure

```
ethos/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI app (v2.0)
│   │   ├── routes/
│   │   │   ├── probe.py                # POST /probe/run
│   │   │   ├── analyze.py              # POST /analyze
│   │   │   ├── reweigh.py              # POST /mitigate/reweigh
│   │   │   ├── citizen.py              # POST /citizen/report
│   │   │   ├── explain.py              # POST /explain
│   │   │   └── recommend.py            # POST /recommend
│   │   └── services/
│   │       ├── probe_service.py        # LLM bias probing engine
│   │       ├── persona_library.py      # India demographic personas
│   │       ├── bias_service.py         # 6 fairness metrics
│   │       ├── reweighing_service.py   # Kamiran & Calders
│   │       ├── firestore_service.py    # Firestore + fallback
│   │       └── gemini_client.py        # Gemini API
├── frontend/
│   └── src/
│       ├── App.jsx                     # SPA: Home, Probe, Audit, Map, Citizen
│       └── styles.css
└── flutter_app/
    └── lib/main.dart                   # Mobile: Home, Report, Bias Map
```

---

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here   # optional
uvicorn app.main:app --reload
# API: http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
```

### Flutter

```bash
cd flutter_app
flutter pub get
flutter run
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | No (demo mode works without it) |
| `GCP_PROJECT_ID` | GCP project for Firestore | No (in-memory fallback) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account JSON path | No |
| `VITE_API_URL` | Backend URL for frontend | No (default: `http://localhost:8000`) |

---

## Deployment

### Cloud Run (Backend)

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/ethos-backend
gcloud run deploy ethos-backend \
  --image gcr.io/PROJECT_ID/ethos-backend \
  --platform managed --region asia-south1 \
  --set-env-vars GEMINI_API_KEY=...,GCP_PROJECT_ID=...
```

### Firebase Hosting (Frontend)

```bash
cd frontend
VITE_API_URL=https://your-cloud-run-url npm run build
firebase deploy
```

### Flutter APK

```bash
cd flutter_app
flutter build apk --dart-define=API_BASE_URL=https://your-cloud-run-url
```

---

## Demo Results

| Dimension | Domain | Group A | Group B | Differential | DIR | Risk |
|-----------|--------|---------|---------|-------------|-----|------|
| Caste | Hiring | Upper-caste: 70% | SC/ST: 35% | +35pp | 0.50 | CRITICAL |
| Religion | Hiring | Hindu: 65% | Muslim: 40% | +25pp | 0.62 | HIGH |
| Gender | Hiring | Male: 60% | Female: 50% | +10pp | 0.83 | MEDIUM |
| Region | Hiring | North Urban: 62% | Northeast: 45% | +17pp | 0.73 | HIGH |

---

## Research Citations

- Bertrand, M. & Mullainathan, S. (2004). "Are Emily and Greg More Employable than Lakisha and Jamal?" *American Economic Review*, 94(4).
- Kamiran, F. & Calders, T. (2012). "Data preprocessing techniques for classification without discrimination." *Knowledge and Information Systems*, 33(1).

---

## India Compliance Framework

| Law | Relevance |
|-----|-----------|
| DPDP Act 2023 | Automated decisions must be explainable and non-discriminatory |
| Articles 15 & 16 | Constitutional prohibition on discrimination by caste, religion, sex, region |
| RBI Fair Practices Code | Non-discriminatory mandate for lending algorithms |
| EEOC Four-Fifths Rule | Selection rate below 80% of highest group triggers disparate impact |
