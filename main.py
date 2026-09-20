import json
import uuid
import re
import io
import csv
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Set to True if you have an OpenAI API key installed
USE_REAL_OPENAI = False

if USE_REAL_OPENAI:
    import openai
    # openai.api_key = "your-api-key-here"

app = FastAPI(
    title="AI Lead Discovery Platform",
    description="Full lead discovery engine with AI scoring and CSV export capabilities.",
    version="2.0.0"
)

# ==========================================
# DATA MODELS
# ==========================================

class NaturalICPRequest(BaseModel):
    prompt: str = Field(
        ..., 
        description="The natural language ICP prompt",
        json_schema_extra={"example": "We sell cybersecurity tools to mid-market fintech companies in North America with 100 to 500 employees targeting CISOs."}
    )

class StructuredICP(BaseModel):
    industry: List[str]
    company_size_min: int
    company_size_max: int
    target_roles: List[str]
    keywords: List[str]
    location: Optional[str] = "Global"

class Lead(BaseModel):
    id: str
    company_name: str
    website: str
    contact_name: str
    contact_role: str
    email: Optional[str] = None
    industry: str
    company_size: int
    location: str
    score: float = 0.0
    score_explanation: str = ""

class LeadDiscoveryResponse(BaseModel):
    icp: StructuredICP
    total_found: int
    leads: List[Lead]

# In-memory database cache for demo export
LATEST_LEADS_CACHE: List[Lead] = []

# ==========================================
# CORE ENGINES
# ==========================================

class ICPEngine:
    @staticmethod
    def parse(prompt: str) -> StructuredICP:
        if USE_REAL_OPENAI:
            # Real LLM parsing logic
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "Extract structured ICP parameters in JSON with keys: industry (list), company_size_min (int), company_size_max (int), target_roles (list), keywords (list), location (string)."
                }, {"role": "user", "content": prompt}]
            )
            data = json.loads(response.choices[0].message.content)
            return StructuredICP(**data)
        
        # Rule-based fallback
        lowered = prompt.lower()
        industries = ["Fintech"] if "fintech" in lowered else ["Technology"]
        roles = ["CISO"] if "ciso" in lowered else ["Decision Maker"]
        
        return StructuredICP(
            industry=industries,
            company_size_min=100 if "100" in lowered else 50,
            company_size_max=500 if "500" in lowered else 1000,
            target_roles=roles,
            keywords=["security", "cloud"],
            location="North America" if "north america" in lowered else "Global"
        )

class LeadDiscoveryEngine:
    @staticmethod
    def search(icp: StructuredICP) -> List[dict]:
        return [
            {
                "company_name": "SecurePay Inc",
                "website": "securepay.io",
                "contact_name": "Sarah Jenkins",
                "contact_role": "CISO",
                "industry": "Fintech",
                "company_size": 250,
                "location": "North America",
                "email": None
            },
            {
                "company_name": "SecurePay Inc", # Duplicate entry test
                "website": "www.securepay.io/",
                "contact_name": "Sarah Jenkins",
                "contact_role": "CISO",
                "industry": "Fintech",
                "company_size": 250,
                "location": "North America",
                "email": "s.jenkins@securepay.io"
            },
            {
                "company_name": "DataVault Tech",
                "website": "datavault.com",
                "contact_name": "David Chen",
                "contact_role": "VP of Engineering",
                "industry": "SaaS",
                "company_size": 420,
                "location": "North America",
                "email": None
            }
        ]

class EnrichmentDeduplicationService:
    @staticmethod
    def normalize_url(url: str) -> str:
        clean = re.sub(r'https?://', '', url.lower())
        clean = re.sub(r'www\.', '', clean)
        return clean.strip('/')

    @classmethod
    def process(cls, raw_leads: List[dict]) -> List[Lead]:
        seen_domains = set()
        processed: List[Lead] = []

        for item in raw_leads:
            domain = cls.normalize_url(item["website"])
            if domain in seen_domains:
                continue
            seen_domains.add(domain)

            email = item.get("email")
            if not email and item.get("contact_name"):
                name_part = item["contact_name"].lower().replace(" ", ".")
                email = f"{name_part}@{domain}"

            processed.append(
                Lead(
                    id=str(uuid.uuid4())[:8],
                    company_name=item["company_name"],
                    website=domain,
                    contact_name=item["contact_name"],
                    contact_role=item["contact_role"],
                    email=email,
                    industry=item["industry"],
                    company_size=item["company_size"],
                    location=item["location"]
                )
            )
        return processed

class AIScoringEngine:
    @staticmethod
    def evaluate(lead: Lead, icp: StructuredICP) -> Lead:
        score = 0.0
        reasons = []

        if any(ind.lower() in lead.industry.lower() for ind in icp.industry):
            score += 30
            reasons.append(f"Matches industry ({lead.industry})")

        if icp.company_size_min <= lead.company_size <= icp.company_size_max:
            score += 30
            reasons.append(f"Size within range ({lead.company_size})")

        if any(role.lower() in lead.contact_role.lower() for role in icp.target_roles):
            score += 30
            reasons.append(f"Role ({lead.contact_role}) is target decision-maker")

        if icp.location == "Global" or icp.location.lower() in lead.location.lower():
            score += 10
            reasons.append("Location matches")

        lead.score = score
        lead.score_explanation = "; ".join(reasons) + "."
        return lead

# ==========================================
# API ENDPOINTS
# ==========================================

@app.post("/api/v1/discover-leads", response_model=LeadDiscoveryResponse)
def discover_and_qualify_leads(request: NaturalICPRequest):
    global LATEST_LEADS_CACHE
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="ICP prompt cannot be empty.")

    icp = ICPEngine.parse(request.prompt)
    raw_leads = LeadDiscoveryEngine.search(icp)
    clean_leads = EnrichmentDeduplicationService.process(raw_leads)
    scored_leads = [AIScoringEngine.evaluate(lead, icp) for lead in clean_leads]
    scored_leads.sort(key=lambda x: x.score, reverse=True)

    LATEST_LEADS_CACHE = scored_leads

    return LeadDiscoveryResponse(
        icp=icp,
        total_found=len(scored_leads),
        leads=scored_leads
    )

@app.get("/api/v1/export-csv")
def export_leads_csv():
    """Feature 7: Export qualified leads directly as a CSV file download."""
    if not LATEST_LEADS_CACHE:
        raise HTTPException(status_code=404, detail="No leads available to export. Run /discover-leads first.")

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["ID", "Company Name", "Website", "Contact Name", "Role", "Email", "Industry", "Company Size", "Score", "Explanation"])

    # Rows
    for lead in LATEST_LEADS_CACHE:
        writer.writerow([
            lead.id, lead.company_name, lead.website, lead.contact_name,
            lead.contact_role, lead.email, lead.industry, lead.company_size,
            lead.score, lead.score_explanation
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=qualified_leads.csv"}
    )

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Lead Discovery Engine"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
