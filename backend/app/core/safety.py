import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ArchAI-Audit")

class AuditLogger:
    @staticmethod
    def log_event(event_type: str, user_id: str, details: dict):
        log_entry = {
            "timestamp": time.time(),
            "event": event_type,
            "user": user_id,
            "details": details
        }
        logger.info(f"AUDIT: {log_entry}")

class UsageTracker:
    def __init__(self):
        self.total_tokens = 0

    def track_llm_usage(self, response):
        """Track token usage from LLM response."""
        if hasattr(response, 'usage_metadata'):
            self.total_tokens += response.usage_metadata.get('total_tokens', 0)
