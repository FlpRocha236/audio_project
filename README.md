# 🎧 Audio Splitter Pro — Backend

> REST API Django para separação de stems de áudio via IA

[![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat&logo=python)](https://python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=flat&logo=django&logoColor=white)](https://djangoproject.com/)
[![Celery](https://img.shields.io/badge/Celery-5.6-37814A?style=flat&logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Redis](https://img.shields.io/badge/Redis-7.3-DC382D?style=flat&logo=redis&logoColor=white)](https://redis.io/)
[![AI](https://img.shields.io/badge/AI-Demucs_htdemucs__6s-FF6F00?style=flat)](https://github.com/facebookresearch/demucs)

---

## ✨ Funcionalidades

* **Separação em 6 Stems** — modelo `htdemucs_6s` da Meta: Voz, Bateria, Baixo, Guitarra, Piano e Outros
* **Processamento Assíncrono** — filas Celery + Redis para não bloquear o servidor durante o processamento de IA
* **Mixer de Backing Tracks** — selecione quais stems manter e gere um MP3 mixado via pydub
* **Download do YouTube** — cole um link e o servidor extrai o áudio automaticamente via yt-dlp
* **REST API completa** — endpoints JSON com CORS configurado para consumo pelo frontend Angular
* **Documentação clara** — respostas padronizadas com status, URLs e tratamento de erros

---

## 🛠️ Stack

```
Python 3.13 · Django 6.0 · Celery 5.6 · Redis · Demucs · pydub · yt-dlp · FFmpeg
```

---

## 📡 Endpoints da API

| Método  | Endpoint              | Descrição                                |
| -------- | --------------------- | ------------------------------------------ |
| `GET`  | `/api/upload/`      | Healthcheck da API                         |
| `POST` | `/api/upload/`      | Envia arquivo de áudio para processamento |
| `GET`  | `/api/status/{id}/` | Verifica status e retorna URLs dos stems   |
| `POST` | `/api/mix/{id}/`    | Gera e baixa mix com stems selecionados    |

### Exemplos

**POST /api/upload/**

```
Content-Type: multipart/form-data
Body: title="Charlie Brown Jr", original_audio=<arquivo.mp3>
```

```json
{
  "success": true,
  "separation_id": 10,
  "title": "Charlie Brown Jr",
  "status": "PENDING"
}
```

**GET /api/status/10/**

```json
{
  "separation_id": 10,
  "status": "COMPLETED",
  "stems": {
    "vocals": "http://localhost:8000/media/...",
    "drums":  "http://localhost:8000/media/...",
    "bass":   "http://localhost:8000/media/...",
    "guitar": "http://localhost:8000/media/...",
    "piano":  "http://localhost:8000/media/...",
    "other":  "http://localhost:8000/media/..."
  }
}
```

**POST /api/mix/10/**

```json
{ "tracks": ["drums", "bass", "guitar"] }
```

Retorna arquivo `.mp3` para download direto.

---

## 🚀 Como Executar Localmente

### Pré-requisitos

1. **Python 3.13+**
2. **FFmpeg (Shared Build)** configurado no PATH do sistema
3. **Redis** — Linux/Mac: `sudo apt install redis` · Windows: [Memurai](https://www.memurai.com/)

### Instalação

```bash
git clone https://github.com/FlpRocha236/audio_project.git
cd audio_project

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
```

### Variáveis de ambiente

Cria um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:4200
FFMPEG_PATH=C:\ffmpeg\bin\ffmpeg.exe
REDIS_URL=redis://localhost:6379/0
```

### Iniciando os serviços

Você precisará de **3 terminais** simultâneos:

```bash
# Terminal 1 — Redis (Memurai no Windows)
# Garanta que está rodando na porta 6379

# Terminal 2 — Celery Worker
celery -A audio_project worker -l info --pool=solo

# Terminal 3 — Django
python manage.py runserver
```

Acesse `http://localhost:8000/api/upload/` — deve retornar `{"status": "Audio Splitter API online"}`.

---

## 🏗️ Arquitetura

```
audio_project/
├── audio_project/
│   ├── settings.py     → configurações com python-decouple e CORS
│   ├── urls.py         → rotas principais com prefixo /api/
│   └── celery.py       → configuração do Celery
└── separator/
    ├── models.py       → AudioSeparation com 6 FileFields de stems
    ├── views.py        → upload, check_status, mix_and_download
    ├── tasks.py        → process_audio_task (Celery + Demucs)
    ├── forms.py        → AudioUploadForm
    └── urls.py         → rotas da API
```

---

## 📝 Observações

* **Primeira execução** : o Demucs baixa os modelos da Meta (~150MB). As execuções seguintes usam cache local e são bem mais rápidas.
* **basic-pitch (MIDI)** : incompatível com Python 3.13 no momento — requer TensorFlow que ainda não tem suporte oficial. Funcionalidade temporariamente desativada.
* **Windows** : use `--pool=solo` no Celery para evitar problemas de multiprocessing.

---

## 🔗 Frontend

O frontend Angular que consome esta API está em:
**[github.com/FlpRocha236/audio-splitter-frontend](https://github.com/FlpRocha236/audio-splitter-frontend)**

---

## 👨‍💻 Autor

**Felipe Rocha** · Junior Back-End Developer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Felipe_Rocha-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/felipe-rafael-rocha-4b4081245/)
[![GitHub](https://img.shields.io/badge/GitHub-FlpRocha236-181717?style=flat&logo=github)](https://github.com/FlpRocha236)

---

## 📄 Licença

MIT License
