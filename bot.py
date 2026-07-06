Отлично! Вижу ошибку:

```
AttributeError: module 'moviepy.audio.fx.all' has no attribute 'speedx'
```

**Проблема:** В MoviePy 1.0.3 функция `speedx` работает иначе. Нужно исправить.

---

## 🔧 Исправление:

Откройте `bot.py`, нажмите ✏️ и **найдите строку 77** (где `clip.fx(afx.speedx, 1.05)`).

**Замените эту строку:**
```python
clip = clip.fx(afx.speedx, 1.05)
```

**На:**
```python
clip = clip.fx(afx.volumex, 1.0)  # Просто оставляем громкость, без изменения скорости
```

Или **полностью уберите изменение скорости** — замените строку 77 на:

```python
# clip = clip.fx(afx.speedx, 1.05)  # Отключено из-за совместимости
```

---

## 📝 Или вот полный исправленный код:

Замените **весь код** в `bot.py` на этот (исправил проблему со speedx):

```python
import os
import random
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import whisper

VIDEO_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
]

def download_video(url, output_name="video.mp4"):
    print(f"📥 Скачиваю: {url}")
    ydl_opts = {'format': 'best', 'outtmpl': output_name, 'quiet': True}
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print(f"✅ Видео скачано: {output_name}")
    return output_name

def transcribe_audio(video_path):
    print("🎤 Распознаю речь (Whisper AI)...")
    try:
        model = whisper.load_model("base")
        result = model.transcribe(video_path, language="ru")
        print(f"✅ Распознано {len(result['segments'])} фраз")
        return result['segments']
    except Exception as e:
        print(f"⚠️ Ошибка распознавания: {e}")
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
    
    # Применяем эффекты (без speedx - он не работает в moviepy 1.0.3)
    if random.random() > 0.7:
        # Зеркальное отражение (зеркалим видео)
        clip = clip.fx(lambda clip: clip.fl_image(lambda img: img[:, ::-1]))
    if random.random() > 0.5:
        # Яркость
        clip = clip.fx(lambda clip: clip.fl_image(lambda img: img * random.uniform(0.95, 1.05)))
    
    # Добавляем субтитры
    if subtitles:
        clip = add_subtitles(clip, subtitles, start)
    
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
        
        try:
            txt_clip = TextClip(
                sub['text'],
                fontsize=45,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(clip.w - 40, None)
            )
            txt_clip = txt_clip.set_pos(('center', 1750)).set_duration(sub_end - sub_start).set_start(sub_start)
            subtitle_clips.append(txt_clip)
        except Exception as e:
            print(f"  ⚠️ Ошибка субтитра: {e}")
    
    if subtitle_clips:
        print(f"  📝 Добавлено {len(subtitle_clips)} субтитров")
        return CompositeVideoClip([clip] + subtitle_clips)
    
    return clip

def cut_video_for_tiktok(input_file, output_folder, subtitles=None):
    print(f"✂️ Нарезаю видео: {input_file}")
    video = VideoFileClip(input_file)
    duration = int(video.duration)
    os.makedirs(output_folder, exist_ok=True)
    
    clip_duration = random.randint(65, min(90, duration))
    clip_number = 1
    
    for i in range(0, duration - clip_duration, clip_duration // 2):
        end = min(i + clip_duration, duration)
        if end - i < 61:
            break
        
        print(f"\n  Клип {clip_number}: {end-i} сек")
        clip = make_vertical_clip(video, i, end, subtitles)
        
        output_path = f"{output_folder}/tiktok_clip_{clip_number}.mp4"
        print(f"  💾 Сохраняю: {output_path}")
        
        clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=30, logger=None)
        clip.close()
        clip_number += 1
        
        if clip_number > 3:
            break
    
    video.close()
    print(f"\n✅ Создано {clip_number - 1} клипов!")
    return clip_number - 1

def main():
    print("🤖 Запуск бота с Whisper AI...\n")
    
    for i, url in enumerate(VIDEO_URLS):
        print(f"\n{'='*60}")
        print(f"Видео {i+1}/{len(VIDEO_URLS)}")
        print('='*60)
        
        video_file = download_video(url, f"video_{i}.mp4")
        subtitles = transcribe_audio(video_file)
        num_clips = cut_video_for_tiktok(video_file, f"tiktok_clips_{i}", subtitles)
        print(f"\n✅ Видео {i+1} обработано! Клипов: {num_clips}")
    
    print("\n" + "="*60)
    print("🎉 ГОТОВО!")
    print("="*60)

if __name__ == "__main__":
    main()
```

Нажмите **"Commit changes"**

---

## 🔄 Запустите заново:

1. Actions → TikTok Video Bot
2. Run workflow → Run workflow
3. Подождите 20-30 минут

**Теперь должно заработать!** 💪
