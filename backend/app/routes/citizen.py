from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.citizen import CitizenReportRequest, CitizenReportResponse
from app.services.firestore_service import get_firestore
from app.services.gemini_client import GeminiClient

router = APIRouter(prefix="/citizen", tags=["citizen"])

_gemini = GeminiClient()

RESOURCES = {
    "hiring": [
        {"name": "Ministry of Labour Grievance Portal", "url": "https://labour.gov.in"},
        {"name": "Equal Opportunity Cell Guidelines", "url": "https://dopt.gov.in"},
    ],
    "lending": [
        {"name": "RBI Banking Ombudsman", "url": "https://bankingombudsman.rbi.org.in"},
        {"name": "SEBI SCORES Portal", "url": "https://scores.gov.in"},
    ],
    "education": [
        {"name": "UGC Grievance Portal", "url": "https://www.ugc.ac.in"},
        {"name": "AICTE Grievance Redressal", "url": "https://www.aicte-india.org"},
    ],
    "healthcare": [
        {"name": "National Consumer Disputes Redressal Commission", "url": "https://ncdrc.nic.in"},
        {"name": "National Human Rights Commission", "url": "https://nhrc.nic.in"},
    ],
    "other": [
        {"name": "National Human Rights Commission", "url": "https://nhrc.nic.in"},
        {"name": "Cyber Crime Portal", "url": "https://cybercrime.gov.in"},
    ],
}


@router.post("/report", response_model=CitizenReportResponse)
def submit_citizen_report(request: CitizenReportRequest) -> dict:
    """
    Accept a citizen's report of suspected AI discrimination and return
    a preliminary assessment powered by Gemini + relevant resources.
    """
    assessment = _generate_assessment(request)

    store = get_firestore()
    report_id = store.save_citizen_report({
        "domain": request.domain,
        "bias_type": request.bias_type,
        "state": request.state or "unknown",
        "organization_type": request.organization_type or "unknown",
        "impact": request.impact,
        "consent": request.consent_to_aggregate,
        # description NOT stored for privacy
    })

    resources = RESOURCES.get(request.domain, RESOURCES["other"])

    return {
        "report_id": report_id,
        "preliminary_assessment": assessment,
        "resources": resources,
        "message": (
            "Your report has been anonymously recorded. "
            "It will be included in India's Algorithmic Bias Map (with your consent). "
            "The assessment above is indicative — not legal advice."
        ),
    }


@router.get("/map-data")
def get_map_data() -> dict:
    """Return aggregated, anonymized stats for the Bias Map."""
    store = get_firestore()
    return store.get_citizen_reports_summary()


def _generate_assessment(request: CitizenReportRequest) -> str:
    if _gemini.is_configured:
        prompt = (
            f"You are an expert in algorithmic discrimination in India. "
            f"A citizen has reported the following experience:\n\n"
            f"Domain: {request.domain}\n"
            f"Suspected bias type: {request.bias_type}\n"
            f"State: {request.state or 'not specified'}\n"
            f"Organization type: {request.organization_type or 'not specified'}\n"
            f"Description: {request.description[:500]}\n\n"
            f"Provide a 3-4 sentence preliminary assessment:\n"
            f"1. Does this scenario match documented patterns of {request.bias_type} discrimination in Indian AI systems?\n"
            f"2. What legal protections may apply?\n"
            f"3. What concrete next step should this person take?\n\n"
            f"Be empathetic, specific, and accurate. Note clearly this is preliminary and not legal advice."
        )
        try:
            return _gemini.generate_text(prompt)
        except Exception:
            pass

    # Fallback assessment
    return (
        f"Based on your description, this scenario involves potential {request.bias_type}-based discrimination "
        f"in a {request.domain} context. This type of concern is well-documented in Indian AI systems, "
        f"particularly in {request.domain} decisions where AI models may have learned historical biases "
        f"from training data. Under India's constitutional equality provisions (Articles 15 and 16) and "
        f"the DPDP Act 2023, you may have grounds to request an explanation for the decision. "
        f"We recommend contacting the relevant regulatory body listed below as a first step."
    )
