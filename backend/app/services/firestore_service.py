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

    def get_citizen_reports_summary(self) -> dict[str, Any]:
        """Return anonymized aggregate stats for the Bias Map."""
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

        for r in records:
            bt = r.get("bias_type", "unknown")
            by_type[bt] = by_type.get(bt, 0) + 1
            dom = r.get("domain", "unknown")
            by_domain[dom] = by_domain.get(dom, 0) + 1
            state = r.get("state", "unknown")
            by_state[state] = by_state.get(state, 0) + 1

        return {
            "total_reports": total,
            "by_bias_type": by_type,
            "by_domain": by_domain,
            "by_state": by_state,
        }


# Singleton
_firestore_service: Optional[FirestoreService] = None


def get_firestore() -> FirestoreService:
    global _firestore_service
    if _firestore_service is None:
        _firestore_service = FirestoreService()
    return _firestore_service
