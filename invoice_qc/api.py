from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
import tempfile
from pathlib import Path
import sys

from . import extractor, validator, models

app = FastAPI(title="Invoice QC Service", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "type": exc.__class__.__name__},
    )


@app.get("/")
def root():
    return FileResponse(str(static_dir / "index.html"))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/validate-json")
def validate_json(invoices: List[models.Invoice]):
    return validator.validate_all(invoices)


@app.post("/extract-and-validate-pdfs")
async def extract_and_validate_pdfs(files: List[UploadFile] = File(...)):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        for uploaded_file in files:
            if not uploaded_file.filename.endswith(".pdf"):
                raise HTTPException(status_code=400, detail=f"Not a PDF: {uploaded_file.filename}")
            content = await uploaded_file.read()
            target = tmppath / uploaded_file.filename
            target.write_bytes(content)
        
        invoices = extractor.extract_from_dir(str(tmppath))
        return validator.validate_all(invoices)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
