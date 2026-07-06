import os
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip

# Список видео для обработки (замените на свои ссылки)
VIDEO_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
]

def download_video(url, output_name="video.mp4"):
    print(f"Скачиваю: {url}")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_name,
        'quiet': True,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    print(f"Видео скачано: {output_name}")
    return output_name

def cut_video(input_file, output_folder, clip_duration=60):
    print(f"Нарезаю видео: {input_file}")
    
    video = VideoFileClip(input_file)
    duration = int(video.duration)
    
    os.makedirs(output_folder, exist_ok=True)
    
    clip_number = 1
    for i in range(0, duration, clip_duration):
        start = i
        end = min(i + clip_duration, duration)
        
        print(f"  Создаю клип {clip_number}: {start}-{end} сек")
        
        clip = video.subclip(start, end)
        output_path = f"{output_folder}/clip_{clip_number}.mp4"
        clip.write_videofile(output_path, logger=None, audio_codec='aac')
        
        clip_number += 1
    
    video.close()
    print(f"Создано {clip_number - 1} клипов!")
    return clip_number - 1

def main():
    print("Запуск бота для TikTok...")
    
    for i, url in enumerate(VIDEO_URLS):
        print(f"\n--- Обработка видео {i+1}/{len(VIDEO_URLS)} ---")
        
        video_file = download_video(url, f"video_{i}.mp4")
        num_clips = cut_video(video_file, f"clips_{i}", clip_duration=60)
        
        print(f"Видео {i+1} обработано! Создано клипов: {num_clips}")
    
    print("\nВсе видео обработаны!")

if __name__ == "__main__":
    main()
