from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.supervisor import run_pipeline
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str


# endpoint where we get report metrics
@app.post("/evaluate")
async def evaluate(req: URLRequest):
    result = await run_pipeline(req.url)
    return {
        "status": "success",
        "data": result
    }

# endpoint to download pdf
@app.get("/report/{filename}")
def get_report(filename: str):
    path = f"./download_report/{filename}"

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=filename,
        headers={
            "Content-Disposition": "inline" 
        }
    )