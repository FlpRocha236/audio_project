# 🎧 Audio Splitter Pro

Um ecossistema web avançado para músicos e produtores musicais. O **Audio Splitter Pro** utiliza Inteligência Artificial de ponta para separar músicas em 6 faixas isoladas (stems) e gerar arquivos MIDI automaticamente a partir do áudio, além de permitir o download direto do YouTube e mixagem de *Backing Tracks* em tempo real.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=flat&logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![AI](https://img.shields.io/badge/AI-Demucs_&_Basic_Pitch-FF6F00)

---

## ✨ Funcionalidades Principais

* **Separação Multifaixas (6 Stems):** Utiliza o modelo de IA `htdemucs_6s` da Meta para isolar o áudio em: *Voz, Bateria, Baixo, Guitarra, Piano e Outros/SFX*.
* **Conversão de Áudio para MIDI:** Integração com a rede neural `basic-pitch` do Spotify para transcrever as faixas isoladas (Baixo, Guitarra, Piano, Voz) em arquivos `.mid`, permitindo a leitura em softwares como Guitar Pro e MuseScore.
* **Integração com YouTube:** Cole o link de um vídeo e o servidor baixa o áudio automaticamente (`yt-dlp`) para processamento.
* **Mixer de Backing Tracks:** Interface para o usuário selecionar quais instrumentos deseja manter e gerar um novo arquivo MP3 mixado na hora (via `pydub`).
* **Processamento Assíncrono:** Fila de tarefas em segundo plano garantindo que a interface (UI) não trave enquanto a IA processa o áudio. Status atualizado em tempo real no frontend via polling.
* **UI/UX Premium:** Interface limpa, responsiva e moderna com design Glassmorphism estilo macOS.

---

## 🛠️ Tecnologias e Arquitetura

**Backend:**

* **Django:** Framework principal e roteamento.
* **Celery:** Worker para processamento das filas assíncronas de IA.
* **Redis (Memurai no Windows):** Broker de mensagens para o Celery.
* **PyDub & FFmpeg:** Manipulação, corte e exportação de áudio.
* **yt-dlp:** Extração de áudio do YouTube.

**Inteligência Artificial:**

* **Demucs (Hybrid Transformer):** Separação de fontes de áudio.
* **Basic-Pitch:** Transcrição de áudio para notas MIDI.

**Frontend:**

* HTML5, CSS3 avançado, Vanilla JavaScript (Fetch API para polling de status).

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos

1. **Python 3.13+** instalado.
2. **FFmpeg (Shared Build):** É obrigatório ter a versão "Shared" do FFmpeg (que contém os arquivos `.dll` ou `.so`) configurada nas Variáveis de Ambiente (`PATH`) do sistema operacional para o `torchcodec` exportar os áudios corretamente.
3. **Servidor Redis:** No Linux/Mac (`sudo apt install redis` ou `brew install redis`). No Windows, utilize o [Memurai](https://www.memurai.com/).

### Instalação

1. Clone este repositório:
   ```bash
   git clone [https://github.com/SEU-USUARIO/audio-splitter-pro.git](https://github.com/SEU-USUARIO/audio-splitter-pro.git)
   cd audio-splitter-pro
   ```


2. Crie e ative o ambiente virtual:
   **Bash**

   ```
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```
3. Instale as dependências:
   **Bash**

   ```
   pip install -r requirements.txt
   ```

   *(Nota: O modelo Demucs e o Basic-Pitch instalarão o PyTorch automaticamente. A primeira execução baixará os modelos de IA, o que pode levar alguns minutos).*
4. Aplique as migrações do banco de dados:
   **Bash**

   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

---

## ⚙️ Iniciando os Motores

Para o sistema funcionar com o processamento em segundo plano, você precisará de **3 terminais** abertos simultaneamente:

**Terminal 1: O Broker de Mensagens**

* Garanta que o servidor do Redis (ou Memurai) esteja rodando na porta `6379`.

**Terminal 2: O Worker (Celery)**

* Com o ambiente virtual ativado, inicie o trabalhador que executará a IA:
  **Bash**

  ```
  celery -A audio_project worker -l info --pool=solo
  ```

  *(A flag `--pool=solo` é altamente recomendada para ambientes Windows).*

**Terminal 3: O Servidor Django**

* Com o ambiente virtual ativado, inicie a aplicação web:
  **Bash**

  ```
  python manage.py runserver
  ```

Acesse `http://127.0.0.1:8000` no seu navegador e comece a isolar suas faixas!

---

## 📝 Notas sobre a IA

* A primeira vez que o Celery receber uma música, ele fará o download dos modelos de rede neural da Meta e do Spotify (aprox. 150MB no total). As execuções subsequentes usarão o cache local, sendo significativamente mais rápidas.
