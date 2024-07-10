import telebot  # Импортируем библиотеку для создания Telegram-бота
import yt_dlp  # Импортируем библиотеку для скачивания видео с YouTube
from moviepy.editor import *  # Импортируем библиотеку для работы с видеофайлами
import os  # Импортируем библиотеку для работы с файловой системой
import tempfile  # Импортируем библиотеку для работы с временными файлами и директориями

API_TOKEN = '6906802031:AAHztmYTHWMfGzLmzWgkHZ0ksjxufccz33U'  # Замените на ваш токен от BotFather
bot = telebot.TeleBot(API_TOKEN)  # Инициализируем бота с использованием API токена

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на YouTube видео, и я конвертирую его в MP3.")  # Ответ на команду /start

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text  # Получаем текст сообщения (ожидаем, что это будет ссылка)
    if "youtube.com" in url or "youtu.be" in url:  # Проверяем, содержит ли сообщение ссылку на YouTube
        try:
            bot.reply_to(message, "Видео загружается, подождите...")  # Отправляем сообщение о начале загрузки

            # Использование временной директории для сохранения файлов
            with tempfile.TemporaryDirectory() as tmpdirname:
                ydl_opts = {
                    'format': 'bestaudio/best',  # Выбираем лучший аудиоформат
                    'outtmpl': os.path.join(tmpdirname, 'downloaded_video.%(ext)s'),  # Шаблон имени выходного файла
                    'noplaylist': True,  # Не загружать плейлисты, только одиночные видео
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # Используем yt-dlp для скачивания видео
                    info_dict = ydl.extract_info(url, download=True)  # Извлекаем информацию о видео и скачиваем его
                    video_title = info_dict.get('title', 'audio')  # Получаем название видео

                video_path = os.path.join(tmpdirname, 'downloaded_video.webm')  # Полный путь к скачанному видео
                mp3_filename = f"{video_title}.mp3"  # Создаем имя для MP3 файла, используя название видео
                mp3_path = os.path.join(tmpdirname, mp3_filename)  # Полный путь к MP3 файлу

                if not os.path.exists(video_path):  # Проверка существования видеофайла
                    bot.reply_to(message, "Ошибка: не удалось найти загруженное видео.")  # Отправляем сообщение об ошибке
                    return  # Прекращаем выполнение функции, если файл не найден

                # Конвертируем видео в MP3
                audio = AudioFileClip(video_path)  # Загружаем скачанное видео
                audio.write_audiofile(mp3_path)  # Сохраняем аудиофайл в формате MP3

                # Отправляем MP3 файл пользователю
                with open(mp3_path, 'rb') as audio_file:
                    bot.send_audio(message.chat.id, audio_file)  # Отправляем MP3 файл в чат

            # Удаляем сообщение с ссылкой
            bot.delete_message(message.chat.id, message.message_id)  # Удаляем сообщение пользователя с ссылкой
        except yt_dlp.utils.DownloadError as e:  # Обработка ошибок загрузки видео
            bot.reply_to(message, f"Ошибка при загрузке видео: {e}")  # Сообщение об ошибке загрузки видео
        except Exception as e:  # Обработка всех остальных исключений
            bot.reply_to(message, f"Произошла ошибка: {e}")  # Отправляем сообщение об ошибке
    else:
        bot.reply_to(message, "Пожалуйста, отправьте корректную ссылку на YouTube видео.")  # Сообщение при некорректной ссылке

# Запуск бота
bot.polling()  # Запускаем бота в режиме долгого опроса (long polling)
