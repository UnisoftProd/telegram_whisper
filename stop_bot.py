import subprocess
import sys

def reboot(script_name):
    try:
        # Выполняем команду wmic и получаем список процессов Python
        result = subprocess.run(
            ['wmic', 'process', 'where', "name='python.exe'", 'get', 'ProcessId,CommandLine'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Анализируем вывод
        for line in result.stdout.splitlines():
            if script_name in line:  # Ищем имя скрипта в строке
                parts = line.split()  # Разбиваем строку на части
                pid = parts[-1]  # Последний элемент — это PID
                print(f"Найден процесс с PID {pid} для скрипта {script_name}")
                
                # Завершаем процесс
                subprocess.run(['taskkill', '/PID', pid, '/F'], check=True)
                print(f"Процесс с PID {pid} завершен.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


reboot("diarize.py")
reboot("telebot_audio.py")