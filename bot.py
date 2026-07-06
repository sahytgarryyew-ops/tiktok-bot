import os
import random
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import whisper

VIDEO_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # ЗАМЕНИТЕ НА СВОЮ ССЫЛКУ
]

def download_video(url, output_name="video.mp4"):
    print(f"Downloading: {url}")
    ydl_opts = {'format': 'best', 'outtmpl': output_name, 'quiet': True}
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print(f"Video downloaded: {output_name}")
    return output_name

def transcribe_audio(video_path):
    print("Transcribing audio (Whisper AI)...")
    try:
        model = whisper.load_model("base")
        # Auto-detect language (убрали language="ru")
        result = model.transcribe(video_path)
        print(f"Transcribed {len(result['segments'])} phrases")
        print(f"Language detected: {result.get('language', 'unknown')}")
        
        # Показываем первые 3 фразы для проверки
        for i, segment in enumerate(result['segments'][:3]):
            print(f"  [{segment['start']:.1f}-{segment['end']:.1f}] {segment['text']}")
        
        return result['segments']
    except Exception as e:
        print(f"Transcription error: {e}")
        return []

def make_vertical_clip(video, start, end, subtitles=None):
    clip = video.subclip(start, end)
    w, h = clip.size
    target_ratio = 9/16
    
    if w/h > target_ratio:
        new_w = h * target_ratio
        x1 = (w - new_w) // 2
        clip = clip.crop(x1=x1, y1=0, x2=x1+new_w, y2=h)
    else:
        new_h = w / target_ratio
        y1 = (h - new_h) // 2
        clip = clip.crop(x1=0, y1=y1, x2=w, y2=y1+new_h)
    
    clip = clip.resize(height=1920)
    clip = clip.crop(x1=0, y1=0, x2=1080, y2=1920)
    
    # Apply effects
    if random.random() > 0.7:
        clip = clip.fx(lambda clip: clip.fl_image(lambda img: img[:, ::-1]))
    if random.random() > 0.5:
        clip = clip.fx(lambda clip: clip.fl_image(lambda img: img * random.uniform(0.95, 1.05)))
    
    # Add subtitles
    if subtitles and len(subtitles) > 0:
        print(f"Adding subtitles to clip ({len(subtitles)} phrases)")
        clip = add_subtitles(clip, subtitles, start)
    else:
        print("WARNING: No subtitles to add!")
    
    return clip

def add_subtitles(clip, subtitles, clip_start_time):
    clip_duration = clip.duration
    subtitle_clips = []
    
    for sub in subtitles:
        sub_start = sub['start'] - clip_start_time
        sub_end = sub['end'] - clip_start_time
        
        if sub_end < 0 or sub_start > clip_duration:
            continue
        
        sub_start = max(0, sub_start)
        sub_end = min(clip_duration, sub_end)
        
        if sub_start >= sub_end:
            continue
        
        try:
            # Создаем текстовый клип
            txt_clip = TextClip(
                sub['text'].strip(),
                fontsize=50,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=3,
                method='label'
            )
            
            # Позиция внизу по центру
            txt_clip = txt_clip.set_pos(('center', 1700)).set_duration(sub_end - sub_start).set_start(sub_start)
            subtitle_clips.append(txt_clip)
            
        except Exception as e:
            print(f"Subtitle error: {e}")
    
    if subtitle_clips:
        print(f"Successfully added {len(subtitle_clips)} subtitle clips")
        return CompositeVideoClip([clip] + subtitle_clips)
    else:
        print("WARNING: No subtitle clips created!")
        return clip

def cut_video_for_tiktok(input_file, output_folder, subtitles=None):
    print(f"Cutting video: {input_file}")
    video = VideoFileClip(input_file)
    duration = int(video.duration)
    os.makedirs(output_folder, exist_ok=True)
    
    clip_duration = random.randint(65, min(90, duration))
    clip_number = 1
    
    print(f"Total subtitles available: {len(subtitles) if subtitles else 0}")
    
    for i in range(0, duration - clip_duration, clip_duration // 2):
        end = min(i + clip_duration, duration)
        if end - i < 61:
            break
        
        print(f"\nClip {clip_number}: {end-i} sec (from {i} to {end})")
        clip = make_vertical_clip(video, i, end, subtitles)
        
        output_path = f"{output_folder}/tiktok_clip_{clip_number}.mp4"
        print(f"Saving: {output_path}")
        
        clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=30, logger=None)
        clip.close()
        clip_number += 1
        
        if clip_number > 3:
            break
    
    video.close()
    print(f"\nCreated {clip_number - 1} clips!")
    return clip_number - 1

def main():
    print("Starting TikTok bot with Whisper AI...\n")
    
    for i, url in enumerate(VIDEO_URLS):
        print(f"\n{'='*60}")
        print(f"Video {i+1}/{len(VIDEO_URLS)}")
        print('='*60)
        
        video_file = download_video(url, f"video_{i}.mp4")
        subtitles = transcribe_audio(video_file)
        
        if not subtitles or len(subtitles) == 0:
            print("ERROR: No subtitles generated! Skipping video...")
            continue
        
        num_clips = cut_video_for_tiktok(video_file, f"tiktok_clips_{i}", subtitles)
        print(f"Video {i+1} processed! Clips: {num_clips}")
    
    print("\n" + "="*60)
    print("DONE!")
    print("="*60)

if __name__ == "__main__":
    main()
