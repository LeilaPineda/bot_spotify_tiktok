# 🎵 TikTok Live Spotify Queue Bot

Bot de automatización con interfaz gráfica desarrollado en Python que se conecta en tiempo real al chat de una transmisión de TikTok Live para permitir que la audiencia agregue canciones automáticamente a la cola de reproducción de Spotify mediante el comando `!play` y salte temas con `!skip`.

## 🚀 Características Principales

* **Interfaz Gráfica Intuitiva:** Desarrollado con CustomTkinter y modo oscuro, incluyendo ventana de configuración de credenciales integrada y botón de pausa/reanudar en tiempo real.
* **Escucha en tiempo real:** Captura instantáneamente los comentarios del chat de TikTok Live a través de WebSockets públicos.
* **Integración con Spotify Web API:** Busca la canción solicitada y la inserta en la cola de reproducción activa sin interrumpir el tema actual.
* **Comando de salto opcional (`!skip`):** Permite habilitar o deshabilitar desde la interfaz la opción de que el chat pueda saltar canciones.
* **Manejo de errores y estados:** Control visual del estado de conexión tanto de Spotify como de TikTok directamente en la aplicación.

## 🛠️ Tecnologías Utilizadas

* **Python 3.10+** — Lenguaje base de desarrollo.
* **CustomTkinter** — Interfaz gráfica moderna.
* **TikTokLive** — Cliente WebSocket para la recepción asíncrona de eventos de TikTok.
* **Spotipy** — Librería cliente de Python para consumir la API Web de Spotify con flujo OAuth 2.0.

## 📁 Estructura del Proyecto
   ```text
bot_spotify_tiktok/
│
├── bot_spotify_tiktok.py  # Script principal con la lógica, UI y comandos
├── requirements.txt       # Dependencias del proyecto
├── .gitignore             # Archivos excluidos del control de versiones (claves/tokens)
├── logo.ico               # Icono de la aplicación
└── README.md              # Documentación del proyecto
   ```

## 🔧 Instalación y Configuración

1. **Clonar el repositorio**
   ```bash
   git clone [https://github.com/LeilaPineda/bot_spotify_tiktok.git](https://github.com/LeilaPineda/bot_spotify_tiktok.git)
   cd bot_spotify_tiktok
   
   # Entrar al directorio
   cd bot_spotify_tiktok
   
   # Instalar librerías necesarias
   pip install -r requirements.txt
   ```
   
2. Configurar Spotify Developer Dashboard
* Ingresa a Spotify Developer Dashboard e inicia sesión.
* Haz clic en Create App y llena la información básica.
* En Redirect URIs, agrega exactamente: http://127.0.0.1:8888/callback
* Selecciona la opción Web API y guarda los cambios.
* Copia tu Client ID y Client Secret desde el panel de configuración de la app.

3. Ejecutar la aplicación
```bash
python bot_spotify_tiktok.py
```
* Al abrir la app por primera vez, haz clic en el botón ⚙️ Settings para ingresar tus credenciales de Spotify y tu usuario de TikTok.

## 💻 Uso
1. Abre la aplicación de Spotify en tu PC y pon a sonar cualquier canción por un par de segundos (para fijar un dispositivo activo).
2. Inicia transmisión en vivo en tu cuenta de TikTok.
3. Abre tu bot, verifica que las conexiones estén en verde e inicia la ejecución.
4. Cuando tus espectadores escriban en el chat: !play [Nombre de la canción], el bot la buscará y agregará a la cola automáticamente.

## 🛡️ Licencia
Este proyecto está distribuido bajo la licencia MIT. Consulta el archivo LICENSE para más información.
