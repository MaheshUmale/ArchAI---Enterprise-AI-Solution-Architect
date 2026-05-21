import json
import pandas as pd
from neo4j import GraphDatabase
from app.core.config import settings

class KnowledgeIngestion:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def ingest_json(self, data: dict):
        with self.driver.session() as session:
            # Systems
            for sys in data.get("systems", []):
                session.run("""
                    MERGE (s:System {id: $id})
                    SET s.name = $name, s.type = $type, s.cloud = $cloud,
                        s.owner = $owner, s.status = $status
                """, **sys)

            # Data Assets
            for asset in data.get("data_assets", []):
                session.run("""
                    MERGE (d:DataAsset {id: $id})
                    SET d.name = $name, d.classification = $classification
                """, **asset)

            # Interfaces / Feeds
            for feed in data.get("interfaces", []):
                session.run("""
                    MATCH (src:System {id: $source_id})
                    MATCH (target:System {id: $target_id})
                    MERGE (src)-[r:FEEDS {id: $id}]->(target)
                    SET r.protocol = $protocol, r.frequency = $frequency
                """, **feed)

            # Owners
            for owner in data.get("owners", []):
                session.run("""
                    MERGE (o:Owner {id: $id})
                    SET o.name = $name, o.department = $department
                """, **owner)
                if "system_id" in owner:
                    session.run("""
                        MATCH (s:System {id: $system_id})
                        MATCH (o:Owner {id: $id})
                        MERGE (s)-[:OWNED_BY]->(o)
                    """, **owner)

            # Licenses
            for license in data.get("licenses", []):
                session.run("""
                    MERGE (l:License {id: $id})
                    SET l.name = $name, l.cost = $cost, l.renewal_date = $renewal_date
                """, **license)
                if "system_id" in license:
                    session.run("""
                        MATCH (s:System {id: $system_id})
                        MATCH (l:License {id: $id})
                        MERGE (s)-[:HAS_LICENSE]->(l)
                    """, **license)

            # Policies
            for policy in data.get("policies", []):
                session.run("""
                    MERGE (p:Policy {id: $id})
                    SET p.name = $name, p.description = $description, p.severity = $severity
                """, **policy)

            # Past Decisions
            for decision in data.get("past_decisions", []):
                session.run("""
                    MERGE (d:PastDecision {id: $id})
                    SET d.title = $title, d.context = $context, d.decision = $decision, d.justification = $justification
                """, **decision)

    def ingest_excel(self, file_path: str, sheet_name: str, entity_type: str):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        data = df.to_dict(orient='records')

        with self.driver.session() as session:
            if entity_type == "System":
                for row in data:
                    session.run("MERGE (s:System {id: $id}) SET s.name = $name", **row)
            # Add more types as needed
