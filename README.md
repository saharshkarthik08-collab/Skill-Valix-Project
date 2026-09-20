# 🚀 AI-Powered B2B Lead Discovery & Qualification Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI-4051B5?style=for-the-badge&logo=uvicorn&logoColor=white)](https://www.uvicorn.org/)

---

## 1. Project Overview & Abstract

The modern B2B marketing pipeline is beset by inefficiencies; uncurated, inconsistent domain data in candidate prospect pools. This project develops a modular, service-based platform to automate lead discovery, domain entity de-duplication, contact information enrichment, and multi-criteria algorithmic scoring. Ingests higher-level Natural Language Ideal Customer Profiles (ICPs), produces structured target parameters (industry taxonomy, valuation proxies, geography, stakeholder roles), and works through a parallel pipeline architecture, taking raw candidate entities through domain de-duplication routines, heuristic contact enrichment tools, and a multi-attribute decision analysis (MADA) scoring model to generate empirical match grades and justifications that can be exposed as RESTful API calls or exported in structured metadata formats (JSON, CSV).

---



---

## 3. Installation & Dependencies

### Prerequisites

* **Python:** `3.9` or higher
* **Package Manager:** `pip`

### Environment Setup

### 1.Create and activate a virtual environment:

Bash
* **python** -m venv venv
On Windows:

DOS
venv\Scripts\activate
On macOS / Linux:

Bash
source venv/bin/activate
Install required dependencies:

Bash
pip install fastapi uvicorn pydantic
4. Execution & Server Deployment
To instantiate the application backend locally via Uvicorn ASGI server:

Bash
python main.py
Upon initialization, the ASGI instance will bind to http://0.0.0.0:8000.

5. API Reference & Interface Documentation
OpenAPI Specification (Swagger UI)
The interactive HTTP documentation and schema definitions are served at:

Interactive UI: http://localhost:8000/docs

Alternative Spec (ReDoc): http://localhost:8000/redoc
