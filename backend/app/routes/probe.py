from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.probe import DimensionInfo, ProbeResponse, ProbeRunRequest
from app.services.probe_service import ProbeService

router = APIRouter(prefix="/probe", tags=["probe"])

_probe_service = ProbeService()


@router.post("/run", response_model=ProbeResponse)
async def run_probe(request: ProbeRunRequest) -> dict:
    """
    Run a counterfactual bias probe on an AI system.
    target_type: 'sample' (deterministic bias simulator), 'gemini' (probe Gemini itself),
                 or 'live_api' (probe an external API endpoint).
    """
    try:
        if request.target_type == "sample":
            result = _probe_service.run_sample_probe(
                dimension=request.dimension,
                domain=request.domain,
                n_per_group=min(request.n_per_group, 20),
                group_a_key=request.group_a_key,
                group_b_key=request.group_b_key,
            )

        elif request.target_type == "gemini":
            template = request.prompt_template or _probe_service.get_default_template(request.domain)
            result = await _probe_service.run_gemini_probe(
                prompt_template=template,
                dimension=request.dimension,
                domain=request.domain,
                n_per_group=min(request.n_per_group, 30),
                group_a_key=request.group_a_key,
                group_b_key=request.group_b_key,
            )

        elif request.target_type == "live_api":
            if not request.target_url:
                raise HTTPException(status_code=400, detail="target_url is required for live_api mode")
            template = request.prompt_template or _probe_service.get_default_template(request.domain)
            result = await _probe_service.run_live_probe(
                prompt_template=template,
                target_url=request.target_url,
                dimension=request.dimension,
                domain=request.domain,
                n_per_group=min(request.n_per_group, 30),
                group_a_key=request.group_a_key,
                group_b_key=request.group_b_key,
            )

        else:
            raise HTTPException(status_code=400, detail=f"Unknown target_type: {request.target_type}")

        return result

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Probe failed: {str(exc)}")


@router.get("/dimensions", response_model=list[DimensionInfo])
def list_dimensions() -> list[dict]:
    """Return all available bias dimensions with metadata."""
    return _probe_service.get_available_dimensions()


@router.get("/template/{domain}")
def get_template(domain: str) -> dict:
    """Return the default prompt template for a domain."""
    template = _probe_service.get_default_template(domain)
    return {"domain": domain, "template": template}
