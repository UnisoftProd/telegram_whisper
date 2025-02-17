from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import subprocess
import os
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.by import By

def insert_in_queue(media_queue, message, result):
    first_id = media_queue[0][0].from_user.id
    self_already_was = False
    for i in range(1, len(media_queue)):
        if media_queue[i][0].from_user.id == message.from_user.id:
            self_already_was = True
        if media_queue[i][0].from_user.id == first_id:
            if self_already_was:
                self_already_was = False
                continue
            else:
                media_queue.insert(i, [message, result])
                break
    media_queue.append([message, result])


def convert_to_wav(input_file):
    if not os.path.isfile(input_file):
        print("Файл не найден.")
        return
    if str(input_file).endswith(".wav"):
        return
    # Определение выходного файла с расширением .wav
    output_file = os.path.splitext(input_file)[0] + ".wav"
    try:
        # Выполнение команды ffmpeg для конвертации
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_file, output_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"Файл успешно конвертирован в {output_file}")
        
        # Удаление исходного файла
        os.remove(input_file)
        print(f"Исходный файл {input_file} удалён.")
    
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при конвертации: {e.stderr.decode()}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def remove_after_last_dot(s):
    return s[:s.rfind('.')] if '.' in s else s


def download_streamyard(link, message, media_queue, meida_queue_thread):

    # Настройки браузера
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Без графического интерфейса
    service = Service("chrome-win64/chrome.exe")  # Замените на путь к chromedriver

    # Открытие страницы
    #driver = webdriver.Chrome(service=service, options=chrome_options)
    driver = webdriver.Firefox()
    driver.get(link)
    time.sleep(5)  # Ждём загрузку страницы

    # Поиск потока
    h3 = driver.find_element(By.TAG_NAME, 'h3')

    network_requests = driver.execute_script("return window.performance.getEntries();")

    for request in network_requests:
        url = request["name"]
        if ".m3u8" in url or ".mp4" in url:
            video_url = url
            output_file = f"{h3.text.replace(' ', '_').replace(':', '-')}.mp4"

            # Команда FFmpeg для скачивания
            command = [
                "ffmpeg",
                "-i", video_url,  # Входной файл (ссылка на поток)
                "-c", "copy",     # Без перекодировки
                output_file       # Имя выходного файла
            ]
            # Запуск команды
            subprocess.run(command, check=True)
            convert_to_wav(output_file)
            result = remove_after_last_dot(output_file)
            result += ".wav"
            if media_queue:
                insert_in_queue(media_queue, message, result)
            else:
                media_queue.append([message, result])
            if not meida_queue_thread.is_alive():
                meida_queue_thread.start()

    driver.quit()