import os
import sys
from pathlib import Path

# Ensure project root directory is in sys.path
project_root = str(Path(__file__).resolve().parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.core.video_processor import generate_comparison_video



def main():
    print("=== Video Comparison Generator (CLI) ===")
    
    # Load category tags from input.txt if available
    tags = []
    input_file = Path("input.txt")
    if input_file.exists():
        with open(input_file, "r", encoding="utf-8") as f:
            tags = [line.strip() for line in f if line.strip()]
    
    if not tags:
        tags = ["IQ", "SPEED", "BATTLE IQ", "DURABILITY"]
        print(f"Using default tags: {tags}")

    # Video inputs configuration
    v1_path = os.getenv("VIDEO1_PATH", "video11.mp4")
    v2_path = os.getenv("VIDEO2_PATH", "video22.mp4")
    output_path = "output_video.mp4"

    player1 = "BATMAN"
    player2 = "X-MEN"

    intro_input = input("Enter intro duration in seconds (default 2.0): ").strip()
    try:
        intro_duration = float(intro_input) if intro_input else 2.0
    except ValueError:
        intro_duration = 2.0

    if not os.path.exists(v1_path) or not os.path.exists(v2_path):
        print(f"\n[Warning] Input files '{v1_path}' or '{v2_path}' were not found.")
        print("To run CLI generation, place two vertical MP4 video clips in this directory as 'video11.mp4' and 'video22.mp4'.")
        print("Or run the FastAPI server with: uvicorn backend.app.main:app --reload")
        return

    print(f"\nGenerating comparison video between {player1} and {player2}...")
    result_path = generate_comparison_video(
        video1_path=v1_path,
        video2_path=v2_path,
        player1_name=player1,
        player2_name=player2,
        tags=tags,
        output_path=output_path,
        intro_duration=intro_duration
    )

    print(f"\nSuccess! Video generated at: {result_path}")

if __name__ == "__main__":
    main()

