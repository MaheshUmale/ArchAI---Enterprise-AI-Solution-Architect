# ArchAI Setup Guide

This document provides step-by-step instructions for setting up the ArchAI environment for development and local testing.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Docker & Docker Compose**: For running Neo4j and PostgreSQL.
- **Python 3.11+**: For the backend API.
- **Node.js (v18+) & npm/yarn**: For the Next.js frontend.
- **API Keys**: You will need an `OPENAI_API_KEY` (and optionally a `CLAUDE_API_KEY`).

## 🛠 Step 1: Infrastructure

Start the required database services using Docker Compose.

```bash
docker-compose up -d
```

This will launch:
- **Neo4j**: Accessible at `http://localhost:7474` (User: `neo4j`, Pass: `password123`)
- **PostgreSQL**: Accessible at `localhost:5432` (User: `archai`, Pass: `archai123`)

## 🐍 Step 2: Backend Setup

1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `.env` file in the `backend/` directory:
    ```env
    PROJECT_NAME=ArchAI
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=password123
    DATABASE_URL=postgresql://archai:archai123@localhost:5432/archai
    OPENAI_API_KEY=your_openai_key_here
    ```

5.  **Run the API**:
    ```bash
    uvicorn app.main:app --reload
    ```
    The backend will be available at `http://localhost:8000`.

## ⚛️ Step 3: Frontend Setup

1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Run the development server**:
    ```bash
    npm run dev
    ```
    The frontend will be available at `http://localhost:3000`.

## 🧪 Step 4: Verification

1.  Open `http://localhost:3000` in your browser.
2.  Enter a sample objective like "Integrate CRM with Data Lake".
3.  Click "Generate Design" and wait for the results to appear.

## 🧹 Troubleshooting

- **Neo4j Connection**: Ensure the `NEO4J_URI` in `.env` matches the port mapped in `docker-compose.yml` (default `7687`).
- **Port Conflict**: If port 3000 is in use, Next.js will automatically try 3001. Ensure your API calls in the frontend point to the correct backend port (default 8000).
- **Tailwind Styles**: If styles aren't appearing, ensure `npm install` finished successfully and you are running `npm run dev`.
