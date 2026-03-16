import os
import subprocess
import sys

def main():
    # 1. Força o Celery a rodar sem dar aquele erro de "superuser"
    os.environ['C_FORCE_ROOT'] = '1'

    print(">>> Iniciando migrações do banco de dados...")
    subprocess.run(["python", "manage.py", "migrate"], check=True)

    print(">>> Iniciando o operário Celery (Background)...")
    # Popen roda em segundo plano e junta os logs na tela principal
    subprocess.Popen(["celery", "-A", "audio_project", "worker", "-l", "info", "--pool=solo"])

    print(">>> Iniciando o servidor web Gunicorn (Foreground)...")
    port = os.environ.get("PORT", "8080")
    # run trava a execução aqui mantendo o Gunicorn vivo e respondendo ao site
    subprocess.run(["gunicorn", "audio_project.wsgi", "--bind", f"0.0.0.0:{port}", "--timeout", "120"])

if __name__ == "__main__":
    main()