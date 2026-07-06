import os
import random
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, afx
import whisper

# Список видео для обработки
VIDEO_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
]

def download_video(url, output_name="video.mp4"):
    """Скачивает видео с YouTube"""
    print(f"📥 Скачиваю: {url}")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_name,
        'quiet': True,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    print(f"✅ Видео скачано: {output_name}")
    return output_name

def extract_audio_and_transcribe(video_path):
    """Извлекает аудио и создает субтитры через Whisper"""
    print("🎤 Распознаю речь (Whisper AI)...")
    
    try:
        model = whisper.load_model("base")
        result = model.transcribe(video_path, language="ru")
        print(f"✅ Распознано {len(result['segments'])} фраз")
        return result['segments']
    except Exception as e:
        print(f"⚠️ Ошибка распознавания: {e}")
        return []

def make_vertical_clip(video, start, end, target_duration=65):
    """Создает вертикальный клип с эффектами"""
    
    # Вырезаем кусок
    clip = video.subclip(start, end)
    
    # Делаем вертикальный формат 9:16
    w, h = clip.size
    target_ratio = 9/16
    
    # Обрезаем по центру
    if w/h > target_ratio:
        # Видео шире, обрезаем по бокам
        new_w = h * target_ratio
        x1 = (w - new_w) // 2
        clip = clip.crop(x1=x1, y1=0, x2=x1+new_w, y2=h)
    else:
        # Видео выше, обрезаем сверху/снизу
        new_h = w / target_ratio
        y1 = (h - new_h) // 2
        clip = clip.crop(x1=0, y1=y1, x2=w, y2=y1+new_h)
    
    # Масштабируем до 1080x1920 (TikTok стандарт)
    clip = clip.resize(height=1920)
    clip = clip.crop(x1=0, y1=0, x2=1080, y2=1920)
    
    # Применяем случайные эффекты для уникальности
    effects_applied = []
    
    # 1. Изменение скорости (1.05x - почти незаметно)
    if random.random() > 0.3:
        clip = clip.fx(afx.speedx, 1.05)
        effects_applied.append("speed")
    
    # 2. Зеркальное отражение (30% шанс)
    if random.random() > 0.7:
        clip = clip.fx(afx.time_mirror)
        effects_applied.append("mirror")
    
    # 3. Немного меняем яркость
    if random.random() > 0.5:
        clip = clip.fx(afx.colorx, random.uniform(0.95, 1.05))
        effects_applied.append("brightness")
    
    print(f"  🎨 Применены эффекты: {', '.join(effects_applied) if effects_applied else 'нет'}")
    
    return clip

def add_subtitles(clip, subtitles, clip_start_time):
    """Добавляет субтитры на видео"""
    
    if not subtitles:
        return clip
    
    # Фильтруем субтитры для этого клипа
    clip_subs = [s for s in subtitles 
                 if clip_start_time <= s['start'] < clip_start_time + clip.duration]
    
    if not clip_subs:
        return clip
    
    # Создаем список текстовых клипов
    text_clips = []
    
    for sub in clip_subs:
        start = sub['start'] - clip_start_time
        end = sub['end'] - clip_start_time
        
        if start < 0:
            start = 0
        if end > clip.duration:
            end = clip.duration
        
        # Создаем текстовый клип
        txt_clip = TextClip(
            sub['text'],
            fontsize=50,
            color='white',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(clip.w - 40, None)
        )
        
        # Позиция внизу
        txt_clip = txt_clip.set_pos(('center', 1750)).set_duration(end - start).set_start(start)
        text_clips.append(txt_clip)
    
    # Накладываем субтитры
    if text_clips:
        final_clip = CompositeVideoClip([clip] + text_clips)
        print(f"  📝 Добавлено {len(text_clips)} субтитров")
        return final_clip
    
    return clip

def cut_video_for_tiktok(input_file, output_folder, subtitles=None):
    """Нарезает видео для TikTok с монетизацией"""
    
    print(f"✂️ Нарезаю видео для TikTok: {input_file}")
    
    video = VideoFileClip(input_file)
    duration = int(video.duration)
    
    os.makedirs(output_folder, exist_ok=True)
    
    # Режем на куски 65-90 секунд (для монетизации нужно >60 сек)
    clip_duration = random.randint(65, min(90, duration))
    
    clip_number = 1
    for i in range(0, duration - clip_duration, clip_duration // 2):
        end = min(i + clip_duration, duration)
        
        if end - i < 61:  # Минимум 61 секунда
            break
        
        print(f"\n  Создаю клип {clip_number}: {i}-{end} сек ({end-i} сек)")
        
        # Создаем вертикальный клип с эффектами
        clip = make_vertical_clip(video, i, end, clip_duration)
        
        # Добавляем субтитры
        if subtitles:
            clip = add_subtitles(clip, subtitles, i)
        
        # Сохраняем
        output_path = f"{output_folder}/tiktok_clip_{clip_number}.mp4"
        print(f"  💾 Сохраняю: {output_path}")
        
        clip.write_videofile(
            output_path, 
            codec='libx264',
            audio_codec='aac',
            fps=30,
            logger=None,
            verbose=False
        )
        
        clip.close()
        clip_number += 1
        
        # Делаем 3-5 клипов с видео
        if clip_number > 5:
            break
    
    video.close()
    print(f"\n✅ Создано {clip_number - 1} клипов для TikTok!")
    return clip_number - 1

def main():
    print("🤖 Запуск бота для TikTok (с монетизацией)...\n")
    
    # Загружаем модель Whisper один раз
    print("📥 Загружаю модель распознавания речи...")
    try:
        model = whisper.load_model("base")
        print("✅ Модель загружена\n")
    except Exception as e:
        print(f"⚠️ Ошибка загрузки модели: {e}")
        print("Продолжаю без субтитров...\n")
        model = None
    
    for i, url in enumerate(VIDEO_URLS):
        print(f"\n{'='*60}")
        print(f"Обработка видео {i+1}/{len(VIDEO_URLS)}")
        print('='*60)
        
        # Скачиваем видео
        video_file = download_video(url, f"video_{i}.mp4")
        
        # Распознаем речь для субтитров
        subtitles = []
        if model:
            try:
                result = model.transcribe(video_file, language="ru")
                subtitles = result['segments']
            except Exception as e:
                print(f"⚠️ Не удалось распознать речь: {e}")
        
        # Нарезаем для TikTok
        num_clips = cut_video_for_tiktok(video_file, f"tiktok_clips_{i}", subtitles)
        
        print(f"\n✅ Видео {i+1} обработано! Создано клипов: {num_clips}")
    
    print("\n" + "="*60)
    print("🎉 ВСЕ ВИДЕО ОБРАБОТАНЫ!")
    print("="*60)

if __name__ == "__main__":
    import whisper
    main()
