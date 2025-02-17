import requests
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import subprocess

# Конфигурация
PUBLIC_FOLDER_URL = "https://disk.yandex.ru/d/mVd9jlocLZhvXQ"  # Публичная ссылка на папку
DOWNLOAD_DIR = "./videos"
VIDEO_EXTENSIONS = (".mp4", ".avi", ".mkv", ".mov", ".flv", ".wmv", ".mp3", ".wav", ".m4a", ".webm")


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


def get_retry_session():
    session = requests.Session()
    retry = Retry(
        total=5, backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get_folder_content(public_url,path):
    session = get_retry_session()
    api_url = "https://cloud-api.yandex.net/v1/disk/public/resources"
    if path:
        params = {"public_key": public_url, "path":[path]}
    else:
        params = {"public_key": public_url}
    try:
        response = session.get(api_url, params=params)
        response.raise_for_status()
        return response.json()["_embedded"]["items"]
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении данных: {e}")
        return []


def download_file(file_url, local_path, media_queue, message, meida_queue_thread, media_groups_in_work):
    session = get_retry_session()
    try:
        with session.get(file_url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Скачан файл: {local_path}")
        convert_to_wav(local_path)
        result = remove_after_last_dot(local_path)
        result += ".wav"


        if message.media_group_id in media_groups_in_work.keys():
            media_groups_in_work[message.media_group_id].append(result)
        else:
            media_groups_in_work[message.media_group_id] = [result]


        if media_queue:
            insert_in_queue(media_queue, message, result)
        else:
            media_queue.append([message, result])
        if not meida_queue_thread.is_alive():
            meida_queue_thread.start()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при скачивании файла: {e}")


def process_public_folder(public_url, media_queue, message, meida_queue_thread, bot, media_groups_in_work, local_dir=DOWNLOAD_DIR, path=""):
    items = get_folder_content(public_url, path)
    os.makedirs(local_dir, exist_ok=True)
    for item in items:
        if item["type"] == "dir":
            #new_local_dir = os.path.join(local_dir, item["name"])
            bot.send_message(message.chat.id, (f"Обработка папки: {item['name']}"))
            print(f"Обработка папки: {item['name']}")
            process_public_folder(public_url,  media_queue, message, meida_queue_thread, bot, media_groups_in_work, local_dir="./", path=item["path"])
        elif item["type"] == "file" and item["name"].lower().endswith(VIDEO_EXTENSIONS):
            bot.send_message(message.chat.id, f"Скачивание файла: {item['name']}")
            print(f"Скачивание файла: {item['name']}")
            #download_file(item["file"], os.path.join(local_dir, item["name"]), media_queue, message, meida_queue_thread)
            download_file(item["file"], item["name"], media_queue, message, meida_queue_thread, media_groups_in_work)
        time.sleep(1)  # Пауза между запросами

