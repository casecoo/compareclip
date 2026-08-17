import os
import sys

# Set OpenBLAS/OpenMP single-thread env vars BEFORE importing numpy/moviepy to prevent RAM pool bloat
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import gc
import random
from pathlib import Path
from typing import List, Dict, Optional, Union

import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

# Ensure project root directory is in sys.path
project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from moviepy.editor import (
    VideoFileClip,
    clips_array,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
    concatenate_videoclips
)

from backend.app.core.config import configure_imagemagick, DEFAULT_AUDIO_PATH

# Ensure ImageMagick is configured properly on module import
configure_imagemagick()

def generate_comparison_video(
    video1_path: Union[str, Path],
    video2_path: Union[str, Path],
    player1_name: str,
    player2_name: str,
    tags: List[str],
    output_path: Union[str, Path],
    audio_path: Optional[Union[str, Path]] = None,
    intro_duration: float = 6.0,
    tag_duration: float = 0.6,
    tag_winners: Optional[Dict[str, str]] = None,
    width: int = 480,
    height: int = 854,
    fps: int = 24
) -> str:

    """
    Generates a vertical comparison video ('VS' format) using sequential segment concatenation.
    Extremely lightweight memory footprint (< 100MB RAM) to run reliably on Render 512MB free instances.
    """
    video_clip1 = None
    video_clip2 = None
    audio_clip = None
    final_clip = None
    segments = []
    all_created_clips = []

    if audio_path is None or not os.path.exists(audio_path):
        audio_path = DEFAULT_AUDIO_PATH

    # Total target video duration (~18 seconds)
    total_video_duration = intro_duration + (len(tags) * tag_duration * 2) + tag_duration + 2.0

    try:
        video_clip1 = VideoFileClip(str(video1_path))
        video_clip2 = VideoFileClip(str(video2_path))
        
        # Crop audio track to exact video duration to avoid loading entire audio into RAM
        raw_audio = AudioFileClip(str(audio_path))
        audio_clip = raw_audio.subclip(0, min(total_video_duration, raw_audio.duration))
        all_created_clips.extend([raw_audio, audio_clip])

        # Auto-loop clips if duration is less than 6.0 seconds
        if video_clip1.duration < 6.0:
            video_clip1 = video_clip1.loop(duration=6.0)
        if video_clip2.duration < 6.0:
            video_clip2 = video_clip2.loop(duration=6.0)

        player_list = [player1_name, player2_name]

        # Determine winner for each category tag if not explicitly provided
        if not tag_winners:
            tag_winners = {tag: random.choice(player_list) for tag in tags}

        # Resize inputs to target resolution (480x854 9:16 vertical SD/HD)
        video1 = video_clip1.resize(width=width, height=height)
        video2 = video_clip2.resize(width=width, height=height)

        # Standard subclips for round winner reveals
        org_video1 = video1.subclip(0, min(tag_duration, video1.duration))
        org_video2 = video2.subclip(0, min(tag_duration, video2.duration))

        # Crop top 50% and bottom 50% for vertical split screen
        new_video1 = video1.crop(y1=height * 0.25, y2=height * 0.75)
        new_video2 = video2.crop(y1=height * 0.25, y2=height * 0.75)

        # Base split-screen clip
        split_background = clips_array([[new_video1], [new_video2]])

        # 1. Intro Segment (6.0 seconds)
        intro_split_bg = split_background.subclip(0, min(intro_duration, split_background.duration))
        text_clip1 = (
            TextClip(player1_name, fontsize=22, color='yellow', bg_color='transparent', font="Roboto")
            .set_position(('center', height // 4 - 25))
            .set_duration(intro_duration)
        )
        text_clip2 = (
            TextClip("VS", fontsize=22, color='yellow', bg_color='transparent', font="Roboto")
            .set_position(('center', 'center'))
            .set_duration(intro_duration)
        )
        text_clip3 = (
            TextClip(player2_name, fontsize=22, color='yellow', bg_color='transparent', font="Roboto")
            .set_position(('center', (height * 3) // 4 - 25))
            .set_duration(intro_duration)
        )

        intro_seg = CompositeVideoClip([intro_split_bg, text_clip1, text_clip2, text_clip3]).set_duration(intro_duration)
        segments.append(intro_seg)
        all_created_clips.extend([intro_split_bg, text_clip1, text_clip2, text_clip3, intro_seg])

        current_duration = intro_duration
        player1_score = 0
        player2_score = 0

        # 2. Tag Rounds Segments (9 rounds x 2 sub-segments = 18 sub-segments)
        for tag in tags:
            winner = tag_winners.get(tag, random.choice(player_list))

            # Part A: Category Tag Header (0.6s)
            tag_bg = split_background.subclip(0, min(tag_duration, split_background.duration))
            text_tag = (
                TextClip(tag.upper(), fontsize=22, color='yellow', bg_color='transparent', font="Roboto")
                .set_position(('center', 'center'))
                .set_duration(tag_duration)
            )
            tag_seg = CompositeVideoClip([tag_bg, text_tag]).set_duration(tag_duration)
            segments.append(tag_seg)
            all_created_clips.extend([tag_bg, text_tag, tag_seg])

            # Part B: Winner Reveal & Score (0.6s)
            if winner == player1_name:
                winner_clip = org_video1
                player1_score += 1
            else:
                winner_clip = org_video2
                player2_score += 1

            current_score = f"{player1_score} - {player2_score}"
            text_score = (
                TextClip(current_score, fontsize=22, color='yellow', bg_color='transparent', font="Roboto")
                .set_position(('center', 'center'))
                .set_duration(tag_duration)
            )
            score_seg = CompositeVideoClip([winner_clip, text_score]).set_duration(tag_duration)
            segments.append(score_seg)
            all_created_clips.extend([text_score, score_seg])

            current_duration += (tag_duration * 2)

        # 3. "WINNER?" Climax Segment (0.6s)
        climax_bg = split_background.subclip(0, min(tag_duration, split_background.duration))
        text_climax = (
            TextClip("WINNER?", fontsize=22, color='yellow', bg_color='transparent', font="Roboto")
            .set_position(('center', 'center'))
            .set_duration(tag_duration)
        )
        climax_seg = CompositeVideoClip([climax_bg, text_climax]).set_duration(tag_duration)
        segments.append(climax_seg)
        all_created_clips.extend([climax_bg, text_climax, climax_seg])
        current_duration += tag_duration

        # 4. Final Winner Announcement Segment
        remaining_audio_time = max(1.0, audio_clip.duration - current_duration)
        if player1_score >= player2_score:
            final_winner_source = video1
            final_winner_name = player1_name
        else:
            final_winner_source = video2
            final_winner_name = player2_name

        final_winner_sub = final_winner_source.subclip(0, min(remaining_audio_time, final_winner_source.duration))
        text_winner = (
            TextClip(final_winner_name, fontsize=22, color='yellow', bg_color='transparent', font="Roboto")
            .set_position(('center', 'center'))
            .set_duration(min(remaining_audio_time, 2.0))
        )
        final_winner_seg = CompositeVideoClip([final_winner_sub, text_winner]).set_duration(remaining_audio_time)
        segments.append(final_winner_seg)
        all_created_clips.extend([final_winner_sub, text_winner, final_winner_seg])

        # Chain segments sequentially (never evaluates 35 clips simultaneously)
        concatenated_video = concatenate_videoclips(segments, method="chain")
        all_created_clips.append(concatenated_video)

        if audio_clip:
            final_clip = concatenated_video.set_audio(audio_clip)
        else:
            final_clip = concatenated_video

        # Write output file with low RAM preset, single thread restriction, and max queue limits
        final_clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            fps=fps,
            preset="ultrafast",
            threads=1,
            ffmpeg_params=["-b:v", "900k", "-max_muxing_queue_size", "1024"],
            logger=None
        )

        return str(output_path)

    finally:
        # Resource cleanup to prevent RAM leaks
        for c in all_created_clips:
            try:
                c.close()
            except Exception:
                pass
        if final_clip:
            try:
                final_clip.close()
            except Exception:
                pass
        if video_clip1:
            try:
                video_clip1.close()
            except Exception:
                pass
        if video_clip2:
            try:
                video_clip2.close()
            except Exception:
                pass
        if audio_clip:
            try:
                audio_clip.close()
            except Exception:
                pass
        gc.collect()
