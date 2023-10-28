from pytube import YouTube
import moviepy.editor

def youtube_download(video_url,path):
    # Создайте объект YouTube
    yt = YouTube(video_url)
    # Выберите качество
    resolution=["720p","480p", "360p", "240p", "144p"]
    for i in resolution:
        try:
            video_stream = yt.streams.get_by_resolution(resolution=i)
            break
        except:
            pass

    unvalid_name=yt.title
    name = ''.join(c if c.isalnum() or c in '._-' else '_' for c in unvalid_name)
    # Укажите путь для сохранения видео
    
    # Загрузите видео
    
    video_stream.download(output_path=path,filename=f"{name}.mp4")


    return name

def convert_to_audio(name):
    video=moviepy.editor.VideoFileClip(f"{name}.mp4")
    audio=video.audio
    audio.write_audiofile(f"{name}.mp3")
    video.close()