import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent

# ==============================================================================
# CONFIGURACIÓN DE CREDENCIALES
# Nota: Para desarrollo local o pruebas, ingresa tus credenciales aquí.
# Nunca subas tus claves reales a un repositorio público.
# ==============================================================================
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID", "8640c4aec8e2429d940e6f632f8447bc")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "4120bdc7090e427889b8789c3cf76e56")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
TIKTOK_USERNAME = os.getenv("TIKTOK_USERNAME", "xleiila__")

# Alcance de permisos necesarios en la API de Spotify
SCOPE = "user-modify-playback-state user-read-playback-state"

# Inicialización del cliente de Spotify
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE
    )
)

# Inicialización del cliente de TikTok Live
client: TikTokLiveClient = TikTokLiveClient(unique_id=TIKTOK_USERNAME)


@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    """
    Escuchador de eventos de comentarios en vivo de TikTok.
    Procesa el comando !play para buscar y añadir canciones a la cola de Spotify.
    """
    comment = event.comment.strip()
    user = event.user.nickname

    # Procesamiento del comando !play
    if comment.lower().startswith("!play "):
        search_query = comment[6:].strip()

        if search_query:
            print(f"[Comando !play] {user} solicitó: '{search_query}'")
            try:
                # Búsqueda del track en el catálogo de Spotify
                results = sp.search(q=search_query, limit=1, type="track")
                tracks = results.get("tracks", {}).get("items", [])

                if tracks:
                    track_uri = tracks[0]["uri"]
                    track_name = tracks[0]["name"]
                    artist_name = tracks[0]["artists"][0]["name"]

                    # Enviar la canción a la cola de reproducción activa
                    sp.add_to_queue(uri=track_uri)
                    print(f"[Spotify] Añadida a la cola: {track_name} - {artist_name}")
                else:
                    print(f"[Spotify] No se encontraron resultados para: '{search_query}'")

            except Exception as e:
                print(f"[Error de Spotify]: {e}")
                print("Asegúrate de tener un reproductor activo en Spotify.")


if __name__ == "__main__":
    print(f"Iniciando Bot de TikTok... Escuchando el chat de @{TIKTOK_USERNAME}")
    client.run()