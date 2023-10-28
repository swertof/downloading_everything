from pytube import YouTube
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
import threading

# Функция вычисления процента загрузки
def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percent_complete = (bytes_downloaded / total_size) * 100
    # Обновление лейбла процента загрузки
    process_label.config(text=f"Скачивание: {percent_complete:.2f}% завершено")
    # Обновление полосы загрузки
    progress_bar['value'] = percent_complete
    root.update_idletasks()

resolutions=["720p", "480p", "360p", "240p", "144p"]
# Качаю видео
def youtube_download(video_url,path,audio):
    # Создайте объект YouTube
    yt = YouTube(video_url, on_progress_callback=on_progress)
    if not audio:
        try:
            video_stream = yt.streams.get_by_resolution(resolution=selected_resolution)
            download_format="mp4"
            global resolution_err
            resolution_err=False
            toggle_button_state(Video_button,MP3_button)
        except:
            resolution_error()
    # Или аудио
    elif audio:
        video_stream = yt.streams.get_audio_only()
        download_format="mp3"
        toggle_button_state(MP3_button,Video_button)
    link_entry.delete(0,"end")
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
        resolutin_select.pack()

# Изменение флага форматов на False
def button_released(button):
    if button == MP3_button:
        global MP3
        MP3 = False
    elif button == Video_button:
        global Video
        Video = False
        resolutin_select.forget()

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
    if not resolution_err:
        messagebox.showerror("Ошибка", "Что-то не так, проверь ссылку или попробуй другое качество")
def wrong_format_error():
    messagebox.showerror("Ошибка", "Что-то не так, выбери формат")
def resolution_error():
    messagebox.showerror("Ошибка", "Разрешение не выбрано")
    global resolution_err
    resolution_err=True

# Тело меню редактирования
edit_menu = Menu(menu)
menu.add_cascade(label="Редактировать", menu=edit_menu)
edit_menu.add_command(label="Выделить все (Ctrl+A)", command=select_all)
edit_menu.add_command(label="Копировать (Ctrl+C)", command=copy)
edit_menu.add_command(label="Вставить (Ctrl+V)", command=paste)
edit_menu.add_command(label="Вырезать (Ctrl+X)", command=cut)

link_label = ttk.Label(root, text="Введите ссылку")
link_entry = ttk.Entry(root)

# Бинды на хоткеи
root.bind("Ctrl+v", lambda event=None: paste())
root.bind("Ctrl+c", lambda event=None: copy())
root.bind("Ctrl+a", lambda event=None: select_all())
root.bind("Ctrl+x", lambda event=None: cut())
link_entry.bind("<Button-3>", popup_menu)
root.bind("<Return>", lambda event=None: downloading())

processing = False
def downloading():
    global processing
    if not Video and not MP3:
        wrong_format_error()
    elif MP3:
        if processing == False:
            try:
                processing=True
                link = link_entry.get()
                file_path = filedialog.askdirectory()
                if file_path:
                    youtube_download(link,file_path,True)
                    messagebox.showinfo('Готово','Скачивание завершено, проверьте директорию!')
                    
            except Exception as ex:
                print(ex)
                wrong_link_error()
            processing=False
    elif Video:
        if processing == False:
            try:
                processing = True
                link = link_entry.get()
                file_path = filedialog.askdirectory()
                if file_path:
                    youtube_download(link,file_path,audio=False)
                    messagebox.showinfo('Готово','Скачивание завершено, проверьте директорию!')
            except Exception as ex:
                print(ex)
                wrong_link_error()
            processing = False

def tryna_to_async():
    download_thread = threading.Thread(target=downloading)
    download_thread.daemon = True
    download_thread.start()


download_button = ttk.Button(root, text="Скачать", command=tryna_to_async)



# Расширяю поле чтоб уместилась ссылка
def on_text_change(event):
    event=None
    max_width = 60
    min_width = 20
    entry_width = max(min(len(link_entry.get()) + 1, max_width), min_width)
    link_entry.config(width=entry_width)
link_entry.bind("<KeyRelease>", on_text_change)

format_label = ttk.Label(root, text="Выберете формат")

# Выпадающий список
resolutin_select = ttk.Combobox(root, values=resolutions)
resolutin_select.set("Разрешение")

# Полоса загрузки
progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")


def on_select(event):
    global selected_resolution
    selected_resolution = resolutin_select.get()
# Привязываем обработчик события выбора элемента
resolutin_select.bind("<<ComboboxSelected>>", on_select)
process_label = ttk.Label(root, text="")

link_label.pack()
link_entry.pack()
MP3_button.pack()
Video_button.pack()
download_button.pack()
process_label.pack()
progress_bar.pack()

root.mainloop()
