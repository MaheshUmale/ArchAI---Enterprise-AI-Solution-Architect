import json
from neo4j import GraphDatabase
from app.core.config import settings

class KnowledgeIngestion:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def ingest_json(self, data: dict):
        with self.driver.session() as session:
            # Ingest Systems
            for sys in data.get("systems", []):
                session.run("""
                    MERGE (s:System {id: $id})
                    SET s.name = $name, s.type = $type, s.cloud = $cloud,
                        s.owner = $owner, s.status = $status
                """, **sys)

            # Add more entity ingestion (DataAsset, Interface, License, Policy, etc.)
