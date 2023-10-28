from pytube import YouTube
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
import multiprocessing as mp
from queue import Queue

# Функция вычисления процента загрузки
def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percent_complete = (bytes_downloaded / total_size) * 100
    #process_label.config(text=f"Скачивание: {percent_complete:.2f}% завершено")
    print(f"Скачивание: {percent_complete:.2f}% завершено")
# Качаю видео
def youtube_download(video_url,path,audio):
    # Создайте объект YouTube
    yt = YouTube(video_url, on_progress_callback=on_progress)
    if not audio:
        # Выберите качество
        resolution=["720p","480p", "360p", "240p", "144p"]
        for i in resolution:
            try:
                video_stream = yt.streams.get_by_resolution(resolution=i)
                download_format="mp4"
                break
            except:
                pass
    # Или аудио
    elif audio:
        video_stream = yt.streams.get_audio_only()
        download_format="mp3"
    unvalid_name=yt.title
    name = ''.join(c if c.isalnum() or c in '._-' else '_' for c in unvalid_name)
    video_stream.download(output_path=path,filename=f"{name}.{download_format}")

    return name

root = tk.Tk()
root.title("Скачать видео")
root.geometry("400x400")

# Флаги форматов
MP3=False
Video=False

# Изменение флага форматов на True
def button_pressed(button):
    if button == MP3_button:
        global MP3
        MP3=True
    elif button == Video_button:
        global Video
        Video = True

# Изменение флага форматов на False
def button_released(button):
    if button == MP3_button:
        global MP3
        MP3 = False
    elif button == Video_button:
        global Video
        Video = False

# Нажатие-отжатие кнопок
def toggle_button_state(button, other_button):
    if button['bg'] == "green":
        button.config(relief="sunken", bg="red")
        other_button.config(relief="raised", bg="green")
        button_pressed(button)
        button_released(other_button)
    else:
        button.config(relief="raised", bg="green")   
        button_released(button)

# Создание кнопок
MP3_button = tk.Button(root, text="MP3", relief="raised", bg="green", command = lambda: toggle_button_state(MP3_button,Video_button))
Video_button = tk.Button(root, text="Video", relief="raised", bg="green", command = lambda: toggle_button_state(Video_button,MP3_button))

# Функции меню редактирования
def select_all():
    link_entry.selection_range(0, 'end')
def copy():
    link_entry.event_generate("<<Copy>>")
def paste():
    link_entry.event_generate("<<Paste>>")
def cut():
    link_entry.event_generate("<<Cut>>")
def popup_menu(event):
    edit_menu.post(event.x_root, event.y_root)
menu = Menu(root)
root.config(menu=menu)

# Сообщения и ошибки
def wrong_link_error():
    messagebox.showerror("Ошибка", "Что-то не так, проверь ссылку")
def wrong_format_error():
    messagebox.showerror("Ошибка", "Что-то не так, выбери формат")

# Тело меню редактирования
edit_menu = Menu(menu)
menu.add_cascade(label="Редактировать", menu=edit_menu)
edit_menu.add_command(label="Выделить все (Ctrl+A)", command=select_all)
edit_menu.add_command(label="Копировать (Ctrl+C)", command=copy)
edit_menu.add_command(label="Вставить (Ctrl+V)", command=paste)
edit_menu.add_command(label="Вырезать (Ctrl+X)", command=cut)

link_label = ttk.Label(root, text="Введите ссылку")
link_entry = ttk.Entry(root)

def downloading():
    if not Video and not MP3:
        wrong_format_error()
    elif MP3:
        try:
            link = link_entry.get()
            file_path = filedialog.askdirectory()
            if file_path:
                youtube_download(link,file_path,True)
                messagebox.showinfo('Готово','Скачивание завершено, проверьте директорию!')
                
        except Exception as ex:
            print(ex)
            wrong_link_error()
    elif Video:
        try:
            link = link_entry.get()
            file_path = filedialog.askdirectory()
            if file_path:
                youtube_download(link,file_path,audio=False)
                messagebox.showinfo('Готово','Скачивание завершено, проверьте директорию!')
        except Exception as ex:
            print(ex)
            wrong_link_error()

       
download_button = ttk.Button(root, text="Скачать", command=downloading)

# Бинды на хоткеи
root.bind("Ctrl+v", lambda event=None: paste())
root.bind("Ctrl+c", lambda event=None: copy())
root.bind("Ctrl+a", lambda event=None: select_all())
root.bind("Ctrl+x", lambda event=None: cut())
link_entry.bind("<Button-3>", popup_menu)
root.bind("<Return>", lambda event=None: downloading())

# Расширяю поле чтоб уместилась ссылка
def on_text_change(event):
    max_width = 60
    min_width = 20
    entry_width = max(min(len(link_entry.get()) + 1, max_width), min_width)
    link_entry.config(width=entry_width)
link_entry.bind("<KeyRelease>", on_text_change)

format_label = ttk.Label(root, text="Выберете формат")

process_label = ttk.Label(root, text="")

link_label.pack()
link_entry.pack()
MP3_button.pack()
Video_button.pack()
download_button.pack()
process_label.pack()


root.mainloop()
