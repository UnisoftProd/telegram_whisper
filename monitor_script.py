import psutil
import subprocess
import os
import time
import platform

SCRIPT_NAME = "telebot_audio.py"  # Имя вашего скрипта

def find_python_script(script_name):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                if any(script_name in arg for arg in proc.info['cmdline']):
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None

def kill_existing_script(script_name):
    proc = find_python_script(script_name)
    if proc:
        print(f"Остановка процесса {script_name}: PID {proc.info['pid']}")
        proc.terminate()  # Попытка мягкой остановки
        try:
            proc.wait(timeout=5)
        except psutil.TimeoutExpired:
            print(f"Принудительная остановка процесса: PID {proc.info['pid']}")
            proc.kill()  # Принудительная остановка, если мягкая не сработала
        return True
    return False

def restart_script():
    """Перезапускает скрипт."""
    print(f"Перезапуск {SCRIPT_NAME}...")
    subprocess.Popen([get_python_executable(), SCRIPT_NAME])

def get_python_executable():
    """Возвращает путь к текущему интерпретатору Python."""
    return os.path.basename(os.sys.executable)

def monitor_script():
    """Мониторит и перезапускает скрипт, если он перестал работать."""
    while True:
        if not find_python_script(SCRIPT_NAME):
            restart_script()
        time.sleep(5)  # Интервал проверки состояния скрипта

if __name__ == "__main__":
    # Завершаем старый экземпляр скрипта перед запуском мониторинга
    if kill_existing_script(SCRIPT_NAME):
        time.sleep(3)  # Даем время для корректного завершения старого процесса

    monitor_script()
