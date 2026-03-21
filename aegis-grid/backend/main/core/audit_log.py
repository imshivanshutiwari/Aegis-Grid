"""Immutable Audit Log for tactical decisions.

Every EXECUTE/ABORT decision is recorded with full context:
- Timestamp
- Unit positions at time of decision
- Agent reasoning chain
- Cited ROE documents
- Commander decision
"""
import sqlite3
import json
import time
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("aegis.audit")

DB_PATH = "audit_log.sqlite"


class AuditLogger:
    """SQLite-backed immutable audit log for post-mission analysis."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Create the audit log table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                decision TEXT NOT NULL,
                threat_id TEXT,
                threat_distance_m REAL,
                threat_score REAL,
                assigned_unit TEXT,
                bearing_deg REAL,
                eta_minutes REAL,
                reasoning_chain TEXT,
                cited_documents TEXT,
                unit_snapshot TEXT,
                gps_jammed INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()
        logger.info(f"Audit log initialized at {self.db_path}")

    def log_decision(self, decision: str, context: Dict[str, Any]):
        """Record a tactical decision to the immutable audit log."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        plan = context.get("plan", {})
        threat = context.get("primary_threat", {})
        reasoning = context.get("reasoning_chain", [])
        cited_docs = context.get("cited_documents", [])
        units = context.get("units", [])

        cursor.execute("""
            INSERT INTO audit_log (
                timestamp, decision, threat_id, threat_distance_m, threat_score,
                assigned_unit, bearing_deg, eta_minutes, reasoning_chain,
                cited_documents, unit_snapshot, gps_jammed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            time.time(),
            decision,
            threat.get("unit_id", "UNKNOWN"),
            threat.get("distance_m", 0),
            threat.get("threat_score", 0),
            plan.get("assigned_unit", "NONE"),
            plan.get("bearing_deg", 0),
            plan.get("eta_minutes", 0),
            json.dumps(reasoning),
            json.dumps(cited_docs),
            json.dumps(units[:10]),  # Snapshot of first 10 units
            1 if context.get("gps_jammed", False) else 0
        ))

        conn.commit()
        conn.close()
        logger.info(f"AUDIT LOG: {decision} recorded for threat {threat.get('unit_id', 'UNKNOWN')}")

    def get_recent_decisions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent audit log entries for post-mission review."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, decision, threat_id, threat_distance_m, threat_score,
                   assigned_unit, bearing_deg, eta_minutes, reasoning_chain, cited_documents, gps_jammed
            FROM audit_log ORDER BY timestamp DESC LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "timestamp": row[0],
                "decision": row[1],
                "threat_id": row[2],
                "threat_distance_m": row[3],
                "threat_score": row[4],
                "assigned_unit": row[5],
                "bearing_deg": row[6],
                "eta_minutes": row[7],
                "reasoning_chain": json.loads(row[8]) if row[8] else [],
                "cited_documents": json.loads(row[9]) if row[9] else [],
                "gps_jammed": bool(row[10])
            }
            for row in rows
        ]


# Singleton instance
audit_logger = AuditLogger()
