from moviepy.editor import VideoFileClip

# Kaynak video dosyasının adını belirtin
video_path = "test2.mp4"

# Videoyu yükleyin
clip = VideoFileClip(video_path)

# Yatay ve dikey boyutları değiştirin
new_width, new_height = 720,1280
clip_resized = clip.resize(width=new_width, height=new_height)
clip_resized = clip_resized.subclip(0, 1)

# Yeni videoyu kaydedin
output_path = "outvideo.mp4"
clip_resized.write_videofile(output_path, codec="libx264", audio_codec="aac")
