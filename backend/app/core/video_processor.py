import os
import sys
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
    AudioFileClip
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
    width: int = 1080,
    height: int = 1920,
    fps: int = 24
) -> str:

    """
    Generates a vertical comparison video ('VS' format) between two input video clips
    for a list of category tags.

    Uses `song.mp3` as the default beat-synced audio track.
    """
    video_clip1 = None
    video_clip2 = None
    audio_clip = None
    final_clip = None

    if audio_path is None or not os.path.exists(audio_path):
        audio_path = DEFAULT_AUDIO_PATH

    try:
        video_clip1 = VideoFileClip(str(video1_path))
        video_clip2 = VideoFileClip(str(video2_path))
        audio_clip = AudioFileClip(str(audio_path))

        if video_clip1.duration < 6.0 or video_clip2.duration < 6.0:
            raise ValueError(
                f"Both video clips must be at least 6.0 seconds long (Video 1: {video_clip1.duration:.1f}s, Video 2: {video_clip2.duration:.1f}s)"
            )

        player_list = [player1_name, player2_name]


        # Determine winner for each category tag if not explicitly provided
        if not tag_winners:
            tag_winners = {tag: random.choice(player_list) for tag in tags}

        # Resize inputs to vertical target resolution
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
        intro_split = split_background.subclip(0, min(intro_duration, split_background.duration))

        # Intro text overlays
        text_clip1 = (
            TextClip(player1_name, fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
            .set_position(('center', intro_split.size[1] // 2 - 70))
            .set_duration(intro_duration)
        )
        text_clip2 = (
            TextClip("VS", fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
            .set_position(('center', 'center'))
            .set_duration(intro_duration)
        )
        text_clip3 = (
            TextClip(player2_name, fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
            .set_position(('center', intro_split.size[1] // 2 + 30))
            .set_duration(intro_duration)
        )

        text_video = [text_clip1, text_clip2, text_clip3]
        normal_video = []

        current_duration = intro_duration
        player1_score = 0
        player2_score = 0

        # Build video segments for each category tag
        for tag in tags:
            winner = tag_winners.get(tag, random.choice(player_list))

            # 1. Tag name overlay on split background
            tag_video = split_background.subclip(0, min(tag_duration, split_background.duration)).set_start(current_duration)
            normal_video.append(tag_video)

            text_tag = (
                TextClip(tag.upper(), fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
                .set_start(current_duration)
                .set_position(('center', 'center'))
                .set_duration(tag_duration)
            )
            text_video.append(text_tag)
            current_duration += tag_duration

            # 2. Winner video reveal with current score overlay
            if winner == player1_name:
                temp = org_video1.set_start(current_duration)
                normal_video.append(temp)
                player1_score += 1
                current_score = f"{player1_score} - {player2_score}"
                text_score = (
                    TextClip(current_score, fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
                    .set_start(current_duration)
                    .set_position(('center', 'center'))
                    .set_duration(tag_duration)
                )
                text_video.append(text_score)
            else:
                temp = org_video2.set_start(current_duration)
                normal_video.append(temp)
                player2_score += 1
                current_score = f"{player1_score} - {player2_score}"
                text_score = (
                    TextClip(current_score, fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
                    .set_start(current_duration)
                    .set_position(('center', 'center'))
                    .set_duration(tag_duration)
                )
                text_video.append(text_score)

            current_duration += tag_duration

        # 3. "WINNER?" climax frame
        tag_video = split_background.subclip(0, min(tag_duration, split_background.duration)).set_start(current_duration)
        normal_video.append(tag_video)
        text_tag = (
            TextClip("WINNER?", fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
            .set_start(current_duration)
            .set_position(('center', 'center'))
            .set_duration(tag_duration)
        )
        text_video.append(text_tag)
        current_duration += tag_duration

        # Transition effect
        transition_duration = 0.20
        new_last = [clip.crossfadein(transition_duration) for clip in normal_video]
        new_last.insert(0, intro_split)
        new_last.extend(text_video)

        # 4. Final Winner Announcement Frame
        remaining_audio_time = max(1.0, audio_clip.duration - current_duration)
        if player1_score >= player2_score:
            winner_clip_source = video1
            final_winner_name = player1_name
        else:
            winner_clip_source = video2
            final_winner_name = player2_name

        temp = winner_clip_source.subclip(0, min(remaining_audio_time, winner_clip_source.duration)).set_start(current_duration)
        new_last.append(temp)

        text_winner = (
            TextClip(final_winner_name, fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
            .set_start(current_duration)
            .set_position(('center', 'center'))
            .set_duration(min(remaining_audio_time, 2.0))
        )
        new_last.append(text_winner)

        # Compose final video clip
        final_clip = CompositeVideoClip(new_last)
        if audio_clip:
            final_clip = final_clip.set_audio(audio_clip)

        # Write output file
        final_clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            fps=fps
        )

        return str(output_path)

    finally:
        # Resource cleanup to prevent RAM leaks
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
