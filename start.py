import os
import subprocess
import sys

def main():
    os.environ['C_FORCE_ROOT'] = '1'

    print(">>> Iniciando migrações do banco de dados...")
    subprocess.run(["python", "manage.py", "migrate"], check=True)

    print(">>> Limpando tarefas antigas travadas no banco...")
    # Este comando Python entra no banco e cancela o que travou na queda de energia
    limpeza = "from separator.models import AudioSeparation; AudioSeparation.objects.exclude(status='COMPLETED').update(status='FAILED')"
    subprocess.run(["python", "manage.py", "shell", "-c", limpeza])

    print(">>> Iniciando o operário Celery (Background)...")
    subprocess.Popen(["celery", "-A", "audio_project", "worker", "-l", "info", "--pool=solo"])

    print(">>> Iniciando o servidor web Gunicorn (Foreground)...")
    port = os.environ.get("PORT", "8080")
    subprocess.run(["gunicorn", "audio_project.wsgi", "--bind", f"0.0.0.0:{port}", "--timeout", "120"])

if __name__ == "__main__":
    main()