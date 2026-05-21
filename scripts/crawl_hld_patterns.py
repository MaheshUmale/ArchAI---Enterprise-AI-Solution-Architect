import os
import sys
import json
import asyncio
import argparse
import logging
from typing import List, Dict

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from dotenv import load_dotenv
load_dotenv()

# Attempt to load tools
try:
    from app.agents.base_agent import get_llm
    # We can't import developer tools directly into scripts easily if they require a specific runtime,
    # but we can simulate the search/extract logic.
except ImportError:
    pass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HLD_REPOSITORIES = [
    {
        "name": "Anshul619/HLD-System-Designs",
        "url": "https://github.com/Anshul619/HLD-System-Designs",
        "key_resources": [
            "0_UseCaseDesigns", "1_Databases", "2_MessageBrokersEDA",
            "3_MicroServices", "4_Scalability", "5_HighAvailability",
            "7_ArchitecturePatterns", "8_API-Protocols"
        ]
    },
    {
        "name": "ashishps1/awesome-system-design-resources",
        "url": "https://github.com/ashishps1/awesome-system-design-resources",
        "key_resources": [
            "Scalability", "Availability", "Reliability", "Consistent Hashing",
            "CAP Theorem", "Load Balancing", "API Gateway", "NoSQL",
            "Distributed Caching", "Pub/Sub", "Service Discovery"
        ]
    },
    {
        "name": "donnemartin/system-design-primer",
        "url": "https://github.com/donnemartin/system-design-primer",
        "key_resources": ["Scale from 1 to 11 million users", "Case studies: Twitter, Mint, Pastebin"]
    },
    {
        "name": "vivek-panchal/System-Design-LLD-HLD",
        "url": "https://github.com/vivek-panchal/System-Design-LLD-HLD",
        "key_resources": ["2. HLD-System-Design"]
    }
]

HLD_TEMPLATES = [
    "https://github.com/ARMmbed/mbed-os/blob/master/docs/design-documents/design_template.md",
    "https://www.docuwriter.ai/posts/sample-software-design-document",
    "https://www.ucl.ac.uk/isd/sites/isd/files/migrated-files/HLD_template_v3.docx",
    "https://docs.google.com/document/d/1pgMutdDasJb6eN6yK6M95JM8gQ16IKacxxhPXgeL9WY/edit"
]

async def main():
    parser = argparse.ArgumentParser(description="Gather HLD patterns and templates from curated sources")
    parser.add_argument("--output", type=str, default="backend/data/hld_knowledge_base.json")
    args = parser.parse_args()

    logger.info("Starting HLD Knowledge Gathering (Deep Dive)...")

    knowledge_base = {
        "repositories": HLD_REPOSITORIES,
        "templates": HLD_TEMPLATES,
        "core_elements": [
            "System Architecture Diagram",
            "Component Breakdown",
            "Data Flow Diagrams (DFD)",
            "Technology Stack",
            "Non-Functional Requirements",
            "Scalability Plan",
            "Security & Compliance",
            "Cost Estimation"
        ],
        "curated_patterns": [
            {
                "name": "Microservices with API Gateway",
                "source": "System Design Primer",
                "description": "Standard pattern for scalable backends with centralized auth and routing."
            },
            {
                "name": "Event-Sourcing and CQRS",
                "source": "HLD-System-Designs",
                "description": "Separating read and write models with an immutable event log."
            },
            {
                "name": "Multi-Region Active-Active High Availability",
                "source": "HLD-System-Designs",
                "description": "Deploying services across multiple geographic regions with real-time replication."
            },
            {
                "name": "Content Delivery Network (CDN) with Edge Side Includes",
                "source": "Awesome System Design Resources",
                "description": "Offloading static and dynamic content delivery to the edge for low latency."
            },
            {
                "name": "Distributed Locking with etcd/Zookeeper",
                "source": "HLD-System-Designs",
                "description": "Ensuring mutually exclusive access to shared resources in a distributed cluster."
            }
        ]
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, indent=2)

    logger.info(f"HLD Knowledge Base index saved to {args.output}")

if __name__ == "__main__":
    asyncio.run(main())
