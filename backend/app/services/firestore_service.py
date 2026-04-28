"""
Persistence layer with Firestore as primary store and in-memory dict as fallback.
The in-memory fallback ensures the app works in development without Firebase credentials.
"""

from __future__ import annotations

import datetime
import json
import os
import uuid
from typing import Any, Optional


class FirestoreService:
    def __init__(self) -> None:
        self._db = None
        self._memory: dict[str, dict[str, Any]] = {}
        self._citizen_memory: list[dict[str, Any]] = []
        self._try_init_firestore()

    def _try_init_firestore(self) -> None:
        try:
            from google.cloud import firestore  # type: ignore
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            project = os.getenv("GCP_PROJECT_ID")
            if cred_path or project:
                self._db = firestore.Client(project=project)
        except Exception:
            pass  # Fall through to in-memory mode

    @property
    def using_firestore(self) -> bool:
        return self._db is not None

    # ------------------------------------------------------------------
    # Audit records
    # ------------------------------------------------------------------

    def save_audit(self, audit_id: str, payload: dict[str, Any]) -> None:
        payload = {**payload, "saved_at": datetime.datetime.utcnow().isoformat()}
        if self._db:
            try:
                self._db.collection("audits").document(audit_id).set(payload)
                return
            except Exception:
                pass
        self._memory[audit_id] = payload

    def get_audit(self, audit_id: str) -> Optional[dict[str, Any]]:
        if self._db:
            try:
                doc = self._db.collection("audits").document(audit_id).get()
                return doc.to_dict() if doc.exists else None
            except Exception:
                pass
        return self._memory.get(audit_id)

    def list_audits(self, limit: int = 20) -> list[dict[str, Any]]:
        if self._db:
            try:
                docs = (
                    self._db.collection("audits")
                    .order_by("saved_at", direction="DESCENDING")
                    .limit(limit)
                    .stream()
                )
                return [d.to_dict() for d in docs]
            except Exception:
                pass
        items = sorted(self._memory.values(), key=lambda x: x.get("saved_at", ""), reverse=True)
        return items[:limit]

    # ------------------------------------------------------------------
    # Citizen reports
    # ------------------------------------------------------------------

    def save_citizen_report(self, report: dict[str, Any]) -> str:
        report_id = str(uuid.uuid4())[:8]
        record = {
            "id": report_id,
            "submitted_at": datetime.datetime.utcnow().isoformat(),
            **report,
        }
        if self._db:
            try:
                self._db.collection("citizen_reports").document(report_id).set(record)
                return report_id
            except Exception:
                pass
        self._citizen_memory.append(record)
        return report_id

    # Maps Indian states to their capital city coordinates for map display
    _STATE_CAPITALS: dict[str, tuple[str, float, float]] = {
        "Andhra Pradesh":    ("Amaravati",   16.51, 80.52),
        "Arunachal Pradesh": ("Itanagar",    27.10, 93.62),
        "Assam":             ("Dispur",      26.14, 91.77),
        "Bihar":             ("Patna",       25.59, 85.14),
        "Chhattisgarh":      ("Raipur",      21.25, 81.63),
        "Goa":               ("Panaji",      15.49, 73.83),
        "Gujarat":           ("Gandhinagar", 23.22, 72.68),
        "Haryana":           ("Chandigarh",  30.74, 76.79),
        "Himachal Pradesh":  ("Shimla",      31.10, 77.17),
        "Jharkhand":         ("Ranchi",      23.35, 85.33),
        "Karnataka":         ("Bengaluru",   12.97, 77.59),
        "Kerala":            ("Kochi",        9.93, 76.26),
        "Madhya Pradesh":    ("Bhopal",      23.26, 77.41),
        "Maharashtra":       ("Mumbai",      19.07, 72.87),
        "Manipur":           ("Imphal",      24.82, 93.94),
        "Meghalaya":         ("Shillong",    25.57, 91.89),
        "Mizoram":           ("Aizawl",      23.73, 92.72),
        "Nagaland":          ("Kohima",      25.67, 94.11),
        "Odisha":            ("Bhubaneswar", 20.30, 85.84),
        "Punjab":            ("Chandigarh",  30.74, 76.79),
        "Rajasthan":         ("Jaipur",      26.91, 75.79),
        "Sikkim":            ("Gangtok",     27.33, 88.62),
        "Tamil Nadu":        ("Chennai",     13.08, 80.27),
        "Telangana":         ("Hyderabad",   17.38, 78.46),
        "Tripura":           ("Agartala",    23.83, 91.28),
        "Uttar Pradesh":     ("Lucknow",     26.85, 80.95),
        "Uttarakhand":       ("Dehradun",    30.32, 78.03),
        "West Bengal":       ("Kolkata",     22.57, 88.36),
        "Delhi":             ("Delhi",       28.60, 77.20),
        "Other":             ("Delhi",       28.60, 77.20),
    }

    def get_citizen_reports_summary(self) -> dict[str, Any]:
        """Return anonymized aggregate stats for the Bias Map, with city coordinates."""
        if self._db:
            try:
                docs = list(self._db.collection("citizen_reports").stream())
                records = [d.to_dict() for d in docs]
            except Exception:
                records = self._citizen_memory
        else:
            records = self._citizen_memory

        total = len(records)
        by_type: dict[str, int] = {}
        by_domain: dict[str, int] = {}
        by_state: dict[str, int] = {}
        # Aggregate per state: {state: {total, by_type, by_domain}}
        state_agg: dict[str, dict] = {}

        for r in records:
            bt = r.get("bias_type", "unknown")
            by_type[bt] = by_type.get(bt, 0) + 1
            dom = r.get("domain", "unknown")
            by_domain[dom] = by_domain.get(dom, 0) + 1
            state = r.get("state", "Other")
            by_state[state] = by_state.get(state, 0) + 1
            if state not in state_agg:
                state_agg[state] = {"total": 0, "by_type": {}, "by_domain": {}}
            state_agg[state]["total"] += 1
            state_agg[state]["by_type"][bt] = state_agg[state]["by_type"].get(bt, 0) + 1
            state_agg[state]["by_domain"][dom] = state_agg[state]["by_domain"].get(dom, 0) + 1

        # Build cities list using state capital coordinates
        cities = []
        for state, agg in state_agg.items():
            coords = self._STATE_CAPITALS.get(state, self._STATE_CAPITALS["Other"])
            city_name, lat, lon = coords
            dominant_type = max(agg["by_type"], key=agg["by_type"].get) if agg["by_type"] else "unknown"
            dominant_domain = max(agg["by_domain"], key=agg["by_domain"].get) if agg["by_domain"] else "unknown"
            cities.append({
                "city":     city_name,
                "state":    state,
                "lat":      lat,
                "lon":      lon,
                "total":    agg["total"],
                "dominant": dominant_type,
                "domain":   dominant_domain,
            })

        return {
            "total_reports": total,
            "by_bias_type":  by_type,
            "by_domain":     by_domain,
            "by_state":      by_state,
            "cities":        cities,
        }


# Singleton
_firestore_service: Optional[FirestoreService] = None


def get_firestore() -> FirestoreService:
    global _firestore_service
    if _firestore_service is None:
        _firestore_service = FirestoreService()
    return _firestore_service
