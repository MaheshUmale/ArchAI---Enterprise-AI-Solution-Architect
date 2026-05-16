KNOWLEDGE_GRAPH_SCHEMA = """
// Constraints for Uniqueness
CREATE CONSTRAINT system_id IF NOT EXISTS FOR (s:System) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT data_asset_id IF NOT EXISTS FOR (d:DataAsset) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT owner_id IF NOT EXISTS FOR (o:Owner) REQUIRE o.id IS UNIQUE;
CREATE CONSTRAINT license_id IF NOT EXISTS FOR (l:License) REQUIRE l.id IS UNIQUE;
CREATE CONSTRAINT policy_id IF NOT EXISTS FOR (p:Policy) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT decision_id IF NOT EXISTS FOR (d:PastDecision) REQUIRE d.id IS UNIQUE;

// Indexes for Search
CREATE INDEX system_name IF NOT EXISTS FOR (s:System) ON (s.name);
CREATE INDEX data_asset_name IF NOT EXISTS FOR (d:DataAsset) ON (d.name);

// Key Relationships:
// (System)-[:FEEDS]->(System)
// (System)-[:OWNED_BY]->(Owner)
// (System)-[:HAS_LICENSE]->(License)
// (System)-[:USES_DATA]->(DataAsset)
// (System)-[:MUST_FOLLOW]->(Policy)
"""
