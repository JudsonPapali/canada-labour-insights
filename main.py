
# backend/main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .data_pipeline import unemployment_timeseries, list_regions

app = FastAPI(title="Canada Labour Insights", version="1.0.0")

# Servir frontend estático (index.html)
static_dir = os.path.join(os.path.dirname(__file__), 'static')
app.mount('/static', StaticFiles(directory=static_dir), name='static')

@app.get('/', response_class=HTMLResponse)
def home():
    index_path = os.path.join(static_dir, 'index.html')
    return FileResponse(index_path)

class SeriesRequest(BaseModel):
    geo: str
    latest_n: int = 24

@app.get('/api/health')
def health():
    return {"status": "ok"}

@app.get('/api/regions')
def regions():
    return {"regions": list_regions()}

@app.get('/api/unemployment')
def get_unemployment(geo: str = "Canada", latest_n: int = 24):
    try:
        df = unemployment_timeseries(geo=geo, latest_n=latest_n)
        return JSONResponse({
            "geo": geo,
            "latest_n": latest_n,
            "series": [{"date": r[0], "value": float(r[1])} for r in df.values]
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

