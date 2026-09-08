import os
import subprocess
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from src.testing.consistency_analyzer import ConsistencyAnalyzer
from src.testing.test_framework import AmmeterTestFramework
from src.testing.error_simulation import ErrorSimulator

app = FastAPI(title="Ammeter Test Server")

# Allow CORS for local React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount results directory so images load properly in the old dashboard
if os.path.exists("results"):
    app.mount("/results", StaticFiles(directory="results"), name="results")

@app.get("/")
def read_root():
    if not os.path.exists("index.html"):
        # Generate it if it doesn't exist
        subprocess.run(["python", "main.py", "--ammeter", "all"], check=True)
    return FileResponse("index.html")

from pydantic import BaseModel, Field
from typing import Optional

class RunParams(BaseModel):
    ammeter: str = Field(default="all", pattern="^(all|greenlee|entes|circutor)$", description="Target ammeter to test")
    count: Optional[int] = Field(default=None, gt=0, description="Number of measurements to take")
    duration: Optional[int] = Field(default=None, gt=0, description="Duration in seconds")
    frequency: Optional[float] = Field(default=None, gt=0.0, description="Sampling frequency in Hz")

@app.post("/api/run")
def api_run(params: RunParams):
    # Run standard tests via programmatic OOP approach
    framework = AmmeterTestFramework("config/config.yaml")
    
    if params.count is not None:
        framework.config.measurements_count = params.count
    if params.duration is not None:
        framework.config.duration_seconds = params.duration
    if params.frequency is not None:
        framework.config.sampling_frequency_hz = params.frequency
        
    ammeters_to_run = ["greenlee", "entes", "circutor"] if params.ammeter == "all" else [params.ammeter]
    
    results = []
    for ammeter in ammeters_to_run:
        result = framework.run_test(ammeter)
        results.append(result)
        
    return JSONResponse({"status": "success", "executed_runs": len(results)})

@app.post("/api/run_errors")
def api_run_errors():
    # Run error simulation suite programmatically
    simulator = ErrorSimulator()
    simulator.run_all()
    return JSONResponse({"status": "success"})

@app.get("/api/runs")
def api_get_runs():
    from src.testing.persistence import PersistenceLayer
    runs_data = PersistenceLayer.get_all_runs()
    return JSONResponse(runs_data)

@app.get("/api/export/{test_id}/{export_type}")
def api_export_run(test_id: str, export_type: str):
    from fastapi import HTTPException
    from src.testing.persistence import PersistenceLayer
    
    run_data = PersistenceLayer.get_run_by_id(test_id)
    if not run_data:
        raise HTTPException(status_code=404, detail="Run not found")
        
    target_dir = run_data.get("_source_dir")
    
    if export_type == "csv":
        file_path = PersistenceLayer.export_csv(run_data, target_dir)
        if file_path and os.path.exists(file_path):
            return FileResponse(file_path, filename=f"data_{test_id}.csv")
            
    elif export_type == "time_series":
        ts_path, _ = PersistenceLayer.export_graphs(run_data, target_dir)
        if ts_path and os.path.exists(ts_path):
            return FileResponse(ts_path, filename=f"time_series_{test_id}.png")
            
    elif export_type == "histogram":
        _, hist_path = PersistenceLayer.export_graphs(run_data, target_dir)
        if hist_path and os.path.exists(hist_path):
            return FileResponse(hist_path, filename=f"histogram_{test_id}.png")
            
    raise HTTPException(status_code=400, detail="Invalid export type or no valid data to plot")


@app.get("/api/consistency")
def api_get_consistency():
    consistency = ConsistencyAnalyzer.analyze_history("results/runs")
    return JSONResponse(consistency)

if __name__ == "__main__":
    from src.testing.emulator_manager import EmulatorManager
    
    # Start the daemon emulator threads natively
    EmulatorManager().start_all_emulators_in_background()
    
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
