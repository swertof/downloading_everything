import os
import telebot
from telebot import types
from telebot_api import *
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
    video=moviepy.editor.VideoFileClip(f"{path}/{name}.mp4")
    audio=video.audio
    audio.write_audiofile(f"{path}/{name}.mp3")
    video.close()

path = '/home/kirill/Документы/GitHub/downloading_everything/STUFF'
bot = telebot.TeleBot(telebot_api)

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton("Аудио MP3")
btn2 = types.KeyboardButton("Видео в документе MP4")
btn3 = types.KeyboardButton("Видео в Телеграм")
markup.add(btn1,btn2,btn3)

Process=""
ID_list=[]
@bot.message_handler(commands=['start'])
def start_message(message):
    
    if Process == "Waiting Link" and message.chat.id in ID_list:
        bot.send_message(message.chat.id, "Не отвлекай меня, качаю видео")
    elif Process == "Waiting Format" and message.chat.id in ID_list:
        bot.send_message(message.chat.id, "Не отвлекай меня, вводи формат")
    elif Process == "Processing" and message.chat.id in ID_list:
        bot.send_message(message.chat.id, "Не отвлекай меня, я работаю")
    else:
        hi_mess=bot.send_message(message.chat.id,"Привет, это телеграмм бот для скачивания с видео YouTube, отправь ссылку на видео")
        bot.register_next_step_handler(hi_mess,request_link)
        ID_list.append(message.chat.id)
        

@bot.message_handler(commands=['text'])
def request_link(message):
    global Process
    Process = "Waiting Link"
    # Получение ссылки на ютуб
    user_link=message.text
    # Ответ пользователю
    bot.send_message(message.chat.id, "Ссылка получена, пробую скачать")
    try:
        global name
        name=youtube_download(user_link, path)
        downloaded=bot.send_message(message.chat.id, "Скачано успешно, выберете формат", reply_markup=markup)
        bot.register_next_step_handler(downloaded,send_file)
    except Exception as ex:
        error_message=bot.send_message(message.chat.id, "Что-то не так, проверь ссылку")
        print(ex)
        bot.register_next_step_handler(error_message, request_link)
    
@bot.message_handler(commands=['text'])
def send_file(message):
    try:
        global Process
        Process = "Waiting Format"
        if message.text == "Видео в Телеграм":
            bot.send_message(message.chat.id, "Отправляю видео, подождите...")
            Process = "Processing"
            file=open(f'{path}/{name}.mp4', 'rb')
            # Отправляем файл пользователю
            bot.send_video(message.chat.id, file, timeout=1000)
            file.close()
            os.remove(f'{path}/{name}.mp4')
            send=bot.send_message(message.chat.id, "Готво, ожидаю новую ссылку")
            bot.register_next_step_handler(send, request_link)

        elif message.text == "Видео в документе MP4":
            bot.send_message(message.chat.id, "Отправляю документ, подождите...")
            Process = "Processing"
            file=open(f'{path}/{name}.mp4', 'rb')
            # Отправляем файл пользователю
            bot.send_document(message.chat.id, file, timeout=1000)
            file.close()
            os.remove(f'{path}/{name}.mp4')
            send=bot.send_message(message.chat.id,"Готво, ожидаю новую ссылку")
            bot.register_next_step_handler(send, request_link)
            

        elif message.text == "Аудио MP3":
            bot.send_message(message.chat.id, "Начинаю конвертировать...")
            Process = "Processing"
            convert_to_audio(name)
            bot.send_message(message.chat.id, "Отправляю mp3, подождите...")
            file=open(f'{path}/{name}.mp3', 'rb')
            # Отправляем файл пользователю
            bot.send_document(message.chat.id, file, timeout=1000)
            file.close()
            os.remove(f'{path}/{name}.mp3')
            os.remove(f'{path}/{name}.mp4')
            send=bot.send_message(message.chat.id, "Готво, ожидаю новую ссылку")
            bot.register_next_step_handler(send, request_link)

        else:
            format_error = bot.send_message(message.chat.id, "Я не знаю таких форматов, попробуйте другой", reply_markup=markup)
            bot.register_next_step_handler(format_error,send_file)
    except Exception as ex:
            print(ex)
            bot.send_message(message.chat.id, "Что-то пошло не так 😰. Наверное файл слишком большой, попробуйте скачать это видео с помощью вот этой программы... ", reply_markup=markup)
            file.close()
            file=open('YT_download.exe', 'rb')
            something_error = bot.send_document(message.chat.id, file, timeout=1000)
            file.close()
            os.remove(f'{path}/{name}.mp4')
            try:
                os.remove(f'{path}/{name}.mp3')
            except:
                pass
            Process = "Waiting Link"
            bot.register_next_step_handler(something_error, request_link)
            
bot.infinity_polling()
