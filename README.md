# 🎵 TikTok Live Spotify Queue Bot

Bot de automatización desarrollado en **Python** que se conecta en tiempo real al chat de una transmisión de **TikTok Live** para permitir que la audiencia agregue canciones automáticamente a la cola de reproducción de **Spotify** utilizando el comando `!play`.

---

## 🚀 Características Principales

* **Escucha en tiempo real:** Captura instantáneamente los comentarios del chat de TikTok Live a través de WebSockets públicos (sin necesidad de credenciales de usuario ni riesgo de suspensión).
* **Integración con Spotify Web API:** Busca la canción solicitada por el usuario e inserta el resultado directo en la lista de espera (queue) activa sin pausar ni interrumpir el tema actual.
* **Fácil configuración:** Diseñado para ejecutarse en segundo plano en tu computadora mientras transmites desde TikTok Live Studio u OBS Studio.
* **Manejo de errores:** Captura búsquedas fallidas o estados donde Spotify no está activo sin interrumpir la ejecución del bot.

---

## 🛠️ Tecnologías Utilizadas

* **[Python 3.10+](https://www.python.org/)** — Lenguaje base de desarrollo.
* **[TikTokLive](https://pypi.org/project/TikTokLive/)** — Cliente WebSocket para la recepción asíncrona de eventos de TikTok.
* **[Spotipy](https://spotipy.readthedocs.io/)** — Librería cliente de Python para consumir la API Web de Spotify con flujo OAuth 2.0.

---

## 📁 Estructura del Proyecto

```text
Bot_Spotify_Tiktok/
│
├── main.py              # Script principal con la lógica del bot y comandos
├── requirements.txt     # Dependencias del proyecto
├── .gitignore           # Archivos excluidos del control de versiones (claves/tokens)
└── README.md            # Documentación del proyecto
```
## 🔧 Instalación y Configuración

1. Clonar el repositorio e instalar dependencias
```bash
# Clonar el repositorio
git clone [https://github.com/TU_USUARIO/tiktok-live-spotify-bot.git](https://github.com/TU_USUARIO/tiktok-live-spotify-bot.git)

# Entrar al directorio
cd tiktok-live-spotify-bot

# Instalar librerías necesarias
pip install -r requirements.txt
```

2. Configurar Spotify Developer Dashboard
Ingresa a Spotify Developer Dashboard e inicia sesión.
Haz clic en Create App y llena la información básica.
En Redirect URIs, agrega exactamente: http://127.0.0.1:8888/callback
Selecciona la opción Web API y guarda los cambios.
Copia tu Client ID y Client Secret desde el panel de configuración de la app.

3. Configurar credenciales en el proyecto
Abre bot_spotify_tiktok.py y asigna tus credenciales en las variables correspondientes (o configúralas mediante variables de entorno):

⚠️ Importante: Asegúrate de incluir .cache y tu CLIENT_SECRET en el archivo .gitignore antes de publicar tu proyecto en repositorios públicos.

## 💻 Uso
1. Abre la aplicación de Spotify en tu PC y pon a sonar cualquier canción por un par de segundos (esto activará tu reproductor).
2. Inicia transmisión en vivo en tu cuenta de TikTok.
3. Ejecuta el archivo principal:
