# ArchAI User Guide

Welcome to ArchAI, your Enterprise AI Solution Architect. This guide will help you get the most out of the platform to generate high-quality, organization-aware architecture designs.

## 🏁 Getting Started

When you first open the ArchAI application, you will be presented with a central objective input area. This is where you describe the architectural problem you want to solve.

## 📝 Writing Effective Objectives

To get the best results from ArchAI, provide clear and specific objectives.

**Good Examples:**
- "Design a real-time data ingestion pipeline from our Oracle CRM to Snowflake using Azure Event Hubs."
- "Create a high-level design for a new customer-facing mobile app API that integrates with our existing Auth0 identity provider."
- "Migrate our legacy on-prem document storage to AWS S3, ensuring all data is encrypted at rest and compliant with GDPR."

**Avoid Vague Objectives:**
- "Build a new app."
- "Integrate systems."

## ⚙️ The Design Process

Once you click **"Generate Design"**, ArchAI's multi-agent system kicks into gear:

1.  **Analysis**: The Orchestrator analyzes your request.
2.  **Knowledge Retrieval**: The Knowledge Agent searches the Enterprise Knowledge Graph for relevant existing systems, licenses, and policies.
3.  **Design Generation**: The Design Agent creates a technical solution, including Mermaid diagrams.
4.  **Review**: The Reviewer Agent critiques the design for security, cost, and compliance.
5.  **Finalization**: The final High-Level Design (HLD) is compiled and presented to you.

## 📊 Interpreting Results

The generated output includes several key sections:

### 1. High-Level Design (HLD)
A detailed textual description of the proposed solution, explaining the "how" and "why" behind the chosen architecture.

### 2. Architecture Diagrams
Visual representations of the design. You can view different perspectives (e.g., Logical, Data Flow, Security) rendered using Mermaid.

### 3. Compliance Summary
A status check indicating how well the design adheres to organization-specific policies and the "Reuse before Buy" principle.

### 4. Confidence Score
A metric from 0-100 indicating the system's certainty in the proposed solution. Scores below 70 may require more manual review or additional context.

## 🛠 Advanced Features

### Ingesting Enterprise Data
To make ArchAI aware of your specific landscape, administrators can upload JSON or Excel files containing:
- System catalogs
- Data asset inventories
- Security policies
- Existing interface registries

### Iterative Design
If the first output isn't perfect, use the chat-like interface to provide feedback (e.g., "Use Kafka instead of Event Hubs") and ArchAI will regenerate the design based on your new constraints.
