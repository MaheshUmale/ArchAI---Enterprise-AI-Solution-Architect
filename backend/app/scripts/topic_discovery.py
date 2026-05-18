import asyncio
from typing import List, Dict
from app.agents.base_agent import get_llm

class TopicDiscovery:
    """
    Agent-driven discovery and prioritization of EA topics for training.
    """
    def __init__(self):
        self.llm = get_llm(temperature=0.3)

    async def generate_topic_list(self, domain: str = "Enterprise Architecture") -> List[Dict]:
        """
        Generates a curated list of authoritative topics and research links.
        """
        prompt = f"""
        You are the ArchAI Knowledge Discovery Agent.
        Generate a list of top 10 authoritative topics and high-quality research areas for {domain}.
        Include:
        - Topic Name
        - Importance for Enterprise Architects
        - Key authoritative sources (e.g., TOGAF, AWS Prescriptive Guidance, Martin Fowler)
        - Suggested links or search queries for deep research.

        Output format: JSON list of objects.
        """

        response = await self.llm.ainvoke(prompt)
        # In a real implementation, we would parse and potentially use a Search tool (e.g. Tavily) to get links.
        return [{"raw": response.content}]

if __name__ == "__main__":
    discovery = TopicDiscovery()
    # To run: python3 -m app.scripts.topic_discovery
    loop = asyncio.get_event_loop()
    topics = loop.run_until_complete(discovery.generate_topic_list())
    print(topics)
