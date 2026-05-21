import time
import logging
import hashlib
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ArchAI-Audit")

class AuditLogger:
    @staticmethod
    def generate_decision_hash(decision_data: dict) -> str:
        """Generates a cryptographic SHA-256 hash for an architectural decision."""
        dump = json.dumps(decision_data, sort_keys=True)
        return hashlib.sha256(dump.encode()).hexdigest()

    @staticmethod
    def log_event(event_type: str, user_id: str, details: dict):
        # If it's a design finalization, sign it
        event_hash = "N/A"
        if event_type == "DESIGN_FINALIZED":
            event_hash = AuditLogger.generate_decision_hash(details)
            details["decision_sig"] = event_hash

        log_entry = {
            "timestamp": time.time(),
            "event": event_type,
            "user": user_id,
            "details": details,
            "hash": event_hash
        }
        logger.info(f"AUDIT: {json.dumps(log_entry)}")

class UsageTracker:
    def __init__(self):
        self.total_tokens = 0

    def track_llm_usage(self, response):
        """Track token usage from LLM response."""
        if hasattr(response, 'usage_metadata'):
            self.total_tokens += response.usage_metadata.get('total_tokens', 0)
