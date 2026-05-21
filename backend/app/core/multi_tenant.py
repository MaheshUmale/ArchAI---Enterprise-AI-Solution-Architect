from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MultiTenantScope:
    """
    Manages scoping for multi-tenant Enterprise Architecture layers.
    Ensures that queries and designs are scoped to specific departments or business units.
    """
    def __init__(self, department_id: Optional[str] = None):
        self.department_id = department_id

    def scope_cypher(self, original_cypher: str) -> str:
        """
        Injects department scoping into a Cypher query.
        """
        if not self.department_id:
            return original_cypher

        # Simple heuristic to add a department filter to node matches
        # In a production system, this would use a proper Cypher parser
        if "WHERE" in original_cypher:
            return original_cypher.replace("WHERE", f"WHERE (n:System OR n:DataAsset) AND n.department_id = '{self.department_id}' AND")
        else:
            return original_cypher + f" MATCH (n) WHERE n.department_id = '{self.department_id}' RETURN n"

    def get_scoped_context(self, context_data: list) -> list:
        """Filters context data based on tenant visibility."""
        if not self.department_id:
            return context_data

        return [item for item in context_data if item.get("department_id") == self.department_id or item.get("is_global")]

multi_tenant_manager = MultiTenantScope()
