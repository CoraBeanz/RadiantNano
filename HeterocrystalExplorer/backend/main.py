from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import uvicorn

# Import our modules
# Note: In a real package we'd use relative imports or install the package
# For this script execution, we might need to adjust sys.path or run as module
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from materials_client import MaterialsClient
from analysis import get_heterojunction_metrics

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="QD-Perovskite Explorer")

# Enable CORS for frontend (still useful if developing separately, but less critical now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize client
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Simple fallback to read .env if python-dotenv is not installed
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    except Exception:
        pass

API_KEY = os.environ.get("MP_API_KEY")
if not API_KEY:
    print("WARNING: MP_API_KEY not found in environment or .env file.")

client = MaterialsClient(API_KEY)

# Mount static files
# We mount to /static to serve css/js, and also serve index.html at root
# Assuming we run from the project root
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("frontend/index.html")


class MaterialSearchRequest(BaseModel):
    formula: str

class HeterojunctionRequest(BaseModel):
    perovskite_formula: str
    qd_formula: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the QD-Perovskite Heterocrystal Explorer API"}

@app.get("/search")
def search_materials(formula: str = Query(..., description="Chemical formula to search")):
    try:
        results = client.search_materials(formula)
        # Remove structure object for JSON serialization
        for r in results:
            r.pop('structure', None)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ScreenRequest(BaseModel):
    max_strain: float = 5.0
    min_perovskite_bandgap: float = 0.0
    max_perovskite_bandgap: float = 5.0
    min_qd_bandgap: float = 0.0
    max_qd_bandgap: float = 5.0

# In-memory cache
CACHE = {
    "perovskites": [],
    "qds": []
}

@app.post("/screen")
def screen_heterojunctions(request: ScreenRequest):
    try:
        # 1. Fetch Candidates (Lazy Load)
        if not CACHE["perovskites"]:
            print("Fetching Perovskites...")
            CACHE["perovskites"] = client.fetch_perovskite_candidates()
            print(f"Cached {len(CACHE['perovskites'])} Perovskites")
            
        if not CACHE["qds"]:
            print("Fetching QDs...")
            CACHE["qds"] = client.fetch_qd_candidates()
            print(f"Cached {len(CACHE['qds'])} QDs")
            
        perovskites = CACHE["perovskites"]
        qds = CACHE["qds"]
        
        results = []
        
        # 2. Filter Candidates by Bandgap individually first to reduce N*M
        valid_ps = [
            p for p in perovskites 
            if request.min_perovskite_bandgap <= p['band_gap'] <= request.max_perovskite_bandgap
        ]
        valid_qs = [
            q for q in qds 
            if request.min_qd_bandgap <= q['band_gap'] <= request.max_qd_bandgap
        ]
        
        # 3. Calculate Pairs
        # Limit total checks to avoid timeout if lists are huge
        # For now, we just iterate.
        
        for p in valid_ps:
            for q in valid_qs:
                # Calculate strain
                strain = get_heterojunction_metrics(p, q)['lattice_mismatch_percent']
                
                if strain <= request.max_strain:
                    results.append({
                        "perovskite": p['formula'],
                        "qd": q['formula'],
                        "strain": strain,
                        "perovskite_bg": round(p['band_gap'], 2),
                        "qd_bg": round(q['band_gap'], 2),
                        "perovskite_id": p['material_id'],
                        "qd_id": q['material_id']
                    })
        
        # Sort by strain
        results.sort(key=lambda x: x['strain'])
        
        return results[:100] # Return top 100 matches
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
def analyze_heterojunction(request: HeterojunctionRequest):
    try:
        # Fetch candidates
        # We take the first stable result or just the first result if no stable ones
        perovskites = client.search_materials(request.perovskite_formula)
        qds = client.search_materials(request.qd_formula)
        
        if not perovskites:
            raise HTTPException(status_code=404, detail=f"No perovskites found for {request.perovskite_formula}")
        if not qds:
            raise HTTPException(status_code=404, detail=f"No QDs found for {request.qd_formula}")
            
        # Prefer stable materials
        p_mat = next((m for m in perovskites if m['is_stable']), perovskites[0])
        q_mat = next((m for m in qds if m['is_stable']), qds[0])
        
        metrics = get_heterojunction_metrics(p_mat, q_mat)
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/material/{material_id}")
def get_material_details(material_id: str):
    try:
        # We can reuse the client's get_material_details method if we exposed it or just use search by ID
        # The client wrapper has get_material_details but it returns a SummaryDoc object.
        # We need to serialize it.
        
        # Let's use the client method we fixed earlier
        doc = client.get_material_details(material_id)
        
        if not doc:
             raise HTTPException(status_code=404, detail="Material not found")
             
        # Serialize
        return {
            "material_id": str(doc.material_id),
            "formula": doc.formula_pretty,
            "band_gap": doc.band_gap,
            "structure": doc.structure.to(fmt="cif"), # Return CIF string for 3D visualization
            "is_stable": doc.is_stable,
            "symmetry": {
                "crystal_system": doc.structure.get_space_group_info()[0],
                "symbol": doc.structure.get_space_group_info()[1]
            },
            "lattice_params": {
                "a": doc.structure.lattice.a,
                "b": doc.structure.lattice.b,
                "c": doc.structure.lattice.c,
                "alpha": doc.structure.lattice.alpha,
                "beta": doc.structure.lattice.beta,
                "gamma": doc.structure.lattice.gamma,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
