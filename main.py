from moviepy.editor import VideoFileClip, clips_array, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.config import change_settings
import random


change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

intro_duration = float(input("Enter the intro duration: "))

tags = []

with open("input.txt",'r') as file:
    for line in file:
        line = line.strip()
        if line:
            tags.append(line)
        
#Setting  players

player_1 = "BATMAN"
player_2 = "X-MEN"

player_list = [player_1,player_2]

player_1_score = 0
player_2_score = 0


#Setting  tags

mydict = {}
for i in range(len(tags)):
    
    mydict[tags[i]] = random.choice(player_list)


print(mydict)



outfile = "output_video.mp4"
audio_path = "song.mp3"



# Load video clips
video_clip1 = VideoFileClip("video11.mp4")
video_clip2 = VideoFileClip("video22.mp4")


#Setting the resolution to the wanted option


video1 = video_clip1.resize(width=1080,height=1920)
video2 = video_clip2.resize(width=1080,height=1920)

org_video1 = video1.subclip(0,0.6)
org_video2 = video2.subclip(0,0.6)


# Cropping each videos (from  %25 to %75)

new_video1 = video1.crop(y1=video1.size[1] * 0.25 , y2=video1.size[1] * 0.75 )
new_video2 = video2.crop(y1=video2.size[1] * 0.25 , y2=video2.size[1] * 0.75 )


final_video = clips_array([[new_video1], [new_video2]])
final_video = final_video.subclip(0,intro_duration)




text_clip1 = TextClip(player_1, fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
text_clip2 = TextClip("VS", fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
text_clip3 = TextClip(player_2, fontsize=30, color='yellow', bg_color='transparent', font="Roboto")


text_clip1 = text_clip1.set_position(('center', final_video.size[1] // 2 - 70)).set_duration(intro_duration)
text_clip2 = text_clip2.set_position(('center', 'center')).set_duration(intro_duration)
text_clip3 = text_clip3.set_position(('center', final_video.size[1] // 2 + 30)).set_duration(intro_duration)


text_video = [text_clip1,text_clip2,text_clip3]
normal_video = []

current_duration = intro_duration


#Giving points to players

for tag,player in mydict.items():

    tag_video = final_video.subclip(0,0.6).set_start(current_duration)

    normal_video.append(tag_video)
    text_tag = TextClip(tag.upper(), fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
    text_tag = text_tag.set_start(current_duration)
    text_tag = text_tag.set_position(('center', 'center')).set_duration(0.6)
    text_video.append(text_tag)
    current_duration += 0.6

    if player == player_1:
        
        temp = org_video1.set_start(current_duration)
        normal_video.append(temp)
        player_1_score += 1
        current_score = f"{player_1_score} - {player_2_score}"
        text_score = TextClip(current_score, fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
        text_score = text_score.set_start(current_duration)
        text_score = text_score.set_position(('center', 'center')).set_duration(0.6)
        normal_video.append(text_score)
        current_duration += 0.6

    else:
        temp = org_video2.set_start(current_duration)
        normal_video.append(temp)
        player_2_score += 1
        current_score = f"{player_1_score} - {player_2_score}"
        text_score = TextClip(current_score, fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
        text_score = text_score.set_start(current_duration)
        text_score = text_score.set_position(('center', 'center')).set_duration(0.6)
        text_video.append(text_score)
        current_duration += 0.6


tag_video = final_video.subclip(0,0.6).set_start(current_duration)
normal_video.append(tag_video)
text_tag = TextClip("WINNER?", fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
text_tag = text_tag.set_start(current_duration)
text_tag = text_tag.set_position(('center', 'center')).set_duration(0.6)
text_video.append(text_tag)
current_duration += 0.6

#Adding crossfade effect to each video's ending

transition_duration = 0.20
new_last = [normal_video[i].crossfadein(transition_duration) for i in range(len(normal_video))]

new_last.insert(0,final_video)

new_last = new_last + text_video


#Loading the audio clip
audio_clip = AudioFileClip(audio_path)


#Showing the result

if player_1_score > player_2_score:
    temp = video1.subclip(0,audio_clip.duration - current_duration).set_start(current_duration)
    new_last.append(temp)
    text_score = TextClip(player_1, fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
    text_score = text_score.set_start(current_duration)
    text_score = text_score.set_position(('center', 'center')).set_duration(1)
    new_last.append(text_score)
else:
    temp = video2.subclip(0,audio_clip.duration - current_duration).set_start(current_duration)
    new_last.append(temp)
    text_score = TextClip(player_2, fontsize=30, color='yellow', bg_color='transparent', font="Roboto")
    text_score = text_score.set_start(current_duration)
    text_score = text_score.set_position(('center', 'center')).set_duration(1)
    new_last.append(text_score)



final_clip = CompositeVideoClip(new_last)

final_clip = final_clip.set_audio(audio_clip)


final_clip.write_videofile(outfile,codec="libx264", audio_codec="aac", fps=24)
