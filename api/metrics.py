from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import numpy as np

# Load telemetry data once
with open("q-vercel-latency") as f:
    telemetry = json.load(f)

class RequestModel(BaseModel):
    regions: List[str]
    threshold_ms: int

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

@app.post("/metrics")
def get_metrics(req: RequestModel):
    result = {}
    for region in req.regions:
        region_data = [r for r in telemetry if r["region"] == region]
        if not region_data:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue
        
        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime_pct"] for r in region_data]
        breaches = sum(1 for l in latencies if l > req.threshold_ms)

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(breaches)
        }
    return result
