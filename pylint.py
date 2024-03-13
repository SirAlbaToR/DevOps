import subprocess
import sys

def main():
    # Путь к файлу или каталогу для проверки pylint
    path_to_check = "/home/danila/downloads/Devops/app.py"

    # Запуск pylint с помощью subprocess
    pylint_process = subprocess.Popen(['pylint', path_to_check], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = pylint_process.communicate()

    # Получение оценки pylint из вывода
    pylint_output = stderr.decode('utf-8')  # pylint выводит сообщения об ошибках в stderr
    pylint_score_line = [line for line in pylint_output.split('\n') if 'Your code has been rated at' in line]
    pylint_score = float(pylint_score_line[0].split()[-2])

    # Проверка оценки pylint и прерывание выполнения сборки с ошибкой, если оценка ниже 5
    if pylint_score < 5:
        print("Оценка pylint ниже 5. Прерывание выполнения сборки с ошибкой.")
        print("##teamcity[buildStatus status='FAILURE' text='Оценка pylint ниже 5']")
        sys.exit(1)

    # Если оценка pylint равна или выше 5, продолжаем выполнение сборки
    print("Оценка pylint равна или выше 5. Продолжение выполнения сборки.")

if __name__ == "__main__":
    main()
