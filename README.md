# Ethos AI - AI Bias Auditing for India

**Does the AI deciding your loan, job, or admission treat your name the same as everyone else's?**

Ethos AI is an open auditing platform that answers this question with statistical rigor. It implements the same counterfactual methodology used in landmark discrimination research: send identical inputs to an AI, vary only the demographic signal, measure the difference. Any disparity is bias, and now it is measurable.

Built for Google Solution Challenge 2026.

---

## The Problem

India has a unique bias landscape that no existing tool addresses:

- IBM AIF360, Microsoft Fairlearn, and Google What-If Tool were built for Western demographics. None probe LLMs, none detect caste bias, none map to Indian law.
- Hiring, lending, education, and healthcare decisions are increasingly made by AI systems trained on historical data that encoded social hierarchies.
- A model trained on 10 years of HR decisions from a company that systematically under-hired SC/ST candidates will inherit that pattern -- not as explicit prejudice, but as a statistical artifact invisible without systematic probing.

Ethos AI fills this gap.

---

## What It Does

### 1. LLM Counterfactual Probe

Send identical prompts to any AI -- Gemini, your own model, or any HTTP endpoint -- changing only the applicant name. The name carries the demographic signal (caste through surname, religion through naming conventions, gender through first name). If the AI's decision rate differs between groups, that is measurable discrimination.

**Methodology:** Bertrand and Mullainathan (2004), "Are Emily and Greg More Employable than Lakisha and Jamal?" -- the original resume audit study, now applied to LLMs.

**Outputs:**
- Acceptance rate per group with statistical significance (Fisher's exact test, p-value)
- Disparate Impact Ratio (EEOC 4/5 rule: threshold 0.80)
- Gemini-powered narrative analysis, remediation plan, and India compliance assessment
- Side-by-side differential examples showing what the AI actually said to each group

**Bias dimensions:** Caste (upper caste vs SC/ST surnames), Religion (Hindu vs Muslim), Gender (male vs female), Region (North Urban vs Northeast India)

**Domains:** HR/Hiring, Bank Lending, University Admissions, Healthcare Triage

### 2. ML Model Fairness Audit

Upload any CSV dataset with a binary outcome column and a sensitive attribute column. Get six statistical fairness metrics instantly:

| Metric | What It Measures |
|--------|------------------|
| Demographic Parity Difference | Raw selection rate gap between groups |
| Disparate Impact Ratio | EEOC 4/5 rule compliance |
| False Positive Rate Difference | Error asymmetry across groups |
| Equal Opportunity Difference | True positive rate gap |
| Average Odds Difference | Combined error rates |
| Theil Index | Outcome inequality (Kamiran & Calders, 2012) |

Download a reweighed dataset with Kamiran-Calders sample weights applied -- a preprocessing debiasing step ready for use in model retraining.

### 3. India AI Bias Map

An anonymised, aggregated map of citizen-reported AI discrimination across Indian states. Every submission stores only the state, domain, and bias type -- no identifying information. As the dataset grows, it becomes evidence that journalists, researchers, and regulators can act on.

---

## India Compliance Framework

Every probe report maps findings to the specific Indian legal instruments that apply:

- **DPDP Act 2023** -- India's data protection law: bias in automated decisions is a data rights violation
- **Articles 15 and 16, Constitution of India** -- prohibition on discrimination by caste, religion, sex, and place of origin applies to algorithmic decision systems
- **RBI Fair Practices Code** -- mandates non-discriminatory lending algorithms for all regulated entities
- **EEOC 4/5 Rule** -- any group with a selection rate below 80% of the highest group is flagged for disparate impact

---

## Architecture

```
Frontend (React + Vite)                 Firebase Hosting (ethos-ca278.web.app)
         |
         | HTTPS
         v
Backend (FastAPI)                       AWS App Runner (auto-scaling container)
   |-- Probe Service                    Gemini 2.0 Flash for narrative analysis
   |-- Audit Service                    pandas + scipy for fairness metrics
   |-- Citizen Service                  Firestore (asia-south1) for reports
```

---

## Running Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
GEMINI_API_KEY=your_key uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
VITE_API_URL=http://localhost:8000 npm run dev
```

**Environment variables:**

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Gemini API key (free tier: 15 RPM; probes are rate-limited to stay within this) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Firebase service account JSON |
| `GCP_PROJECT_ID` | Firebase project ID |

Without these, the app falls back gracefully: in-memory storage replaces Firestore, and the sample mode (deterministic bias simulator) works without any API key.

---

## Sample Dataset

`frontend/public/sample_hiring_dataset.csv` is a synthetic hiring dataset for testing the ML audit. It has a `shortlisted` outcome column and a `caste_group` sensitive attribute, intentionally constructed with a disparate impact ratio below 0.80 to show what a flagged audit looks like.

---

## Live

**Frontend:** https://ethos-ca278.web.app
**API:** https://ccrnsaub9w.us-east-1.awsapprunner.com

---

## Research Foundation

This project applies published, peer-reviewed fairness methodology:

**Bertrand, M. and Mullainathan, S. (2004).** "Are Emily and Greg More Employable than Lakisha and Jamal? A Field Experiment on Labor Market Discrimination." *American Economic Review*, 94(4), 991-1013. doi:10.1257/0002828042002561

The counterfactual probing methodology -- identical resumes, only names changed -- is the direct basis for how Ethos AI probes LLMs. The original experiment used paper resumes; Ethos AI applies the same logic to AI prompts at scale.

**Kamiran, F. and Calders, T. (2012).** "Data Preprocessing Techniques for Classification Without Discrimination." *Knowledge and Information Systems*, 33(1), 1-33. doi:10.1007/s10115-011-0463-8

The reweighing algorithm in the ML audit is directly from this paper. Sample weights are computed to equalise selection rates across sensitive groups before model training.

---

Built by Aadi Joshi for Google Solution Challenge 2026.
