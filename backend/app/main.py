import os
import sys
import json
import shutil
import tempfile
from pathlib import Path
from typing import List

# Ensure project root directory is in sys.path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from backend.app.core.video_processor import generate_comparison_video
from backend.app.core.config import DEFAULT_AUDIO_PATH



app = FastAPI(
    title="Video Comparison Generator API",
    description="API to generate vertical comparison videos ('VS' style) from uploaded video clips.",
    version="1.0.0"
)

# Enable CORS for Vercel frontend and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def cleanup_temp_dir(temp_dir: str):
    """Background task to remove temporary working files after returning response."""
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        print(f"Error cleaning up temp directory {temp_dir}: {e}")

@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "video-comparison-generator"}

@app.post("/api/v1/compare")
async def compare_videos(
    background_tasks: BackgroundTasks,
    video1: UploadFile = File(..., description="First video clip (top half)"),
    video2: UploadFile = File(..., description="Second video clip (bottom half)"),
    player1_name: str = Form("PLAYER 1"),
    player2_name: str = Form("PLAYER 2"),
    categories: str = Form("IQ, BATTLE IQ, SPEED, DURABILITY, STRENGTH, POWER, AGILITY, COMBAT, ENDURANCE")
):
    # Parse categories (supports JSON array string or comma-separated string)
    category_list: List[str] = []
    try:
        parsed = json.loads(categories)
        if isinstance(parsed, list):
            category_list = [str(item).strip() for item in parsed if str(item).strip()]
    except Exception:
        category_list = [cat.strip() for cat in categories.split(",") if cat.strip()]

    if not category_list:
        category_list = ["IQ", "BATTLE IQ", "SPEED", "DURABILITY", "STRENGTH", "POWER", "AGILITY", "COMBAT", "ENDURANCE"]


    # Create temporary directory for input/output files
    temp_dir = tempfile.mkdtemp(prefix="vid_comp_")

    try:
        v1_ext = Path(video1.filename).suffix or ".mp4"
        v2_ext = Path(video2.filename).suffix or ".mp4"

        v1_path = os.path.join(temp_dir, f"input_1{v1_ext}")
        v2_path = os.path.join(temp_dir, f"input_2{v2_ext}")
        out_path = os.path.join(temp_dir, "output.mp4")

        # Save uploaded files to disk
        with open(v1_path, "wb") as buffer:
            shutil.copyfileobj(video1.file, buffer)

        with open(v2_path, "wb") as buffer:
            shutil.copyfileobj(video2.file, buffer)

        # Generate comparison video
        generate_comparison_video(
            video1_path=v1_path,
            video2_path=v2_path,
            player1_name=player1_name,
            player2_name=player2_name,
            tags=category_list,
            output_path=out_path,
            audio_path=DEFAULT_AUDIO_PATH
        )

        if not os.path.exists(out_path):
            raise HTTPException(status_code=500, detail="Video rendering failed to create output file.")

        # Register background cleanup task
        background_tasks.add_task(cleanup_temp_dir, temp_dir)

        return FileResponse(
            path=out_path,
            media_type="video/mp4",
            filename=f"{player1_name}_vs_{player2_name}.mp4"
        )

    except Exception as err:
        cleanup_temp_dir(temp_dir)
        raise HTTPException(status_code=500, detail=f"Error generating video: {str(err)}")
