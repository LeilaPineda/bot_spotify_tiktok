import os
import json
import threading
import sys
import customtkinter as ctk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent
from TikTokLive.client.errors import UserOfflineError

# Archivo JSON local donde se almacenan las credenciales de forma segura
CONFIG_FILE = "config_bot.json"

def resource_path(relative_path):
    """
    Obtiene la ruta absoluta del recurso (como el icono logo.ico), 
    compatible tanto para la ejecución normal en Python como para 
    el archivo ejecutable empaquetado con PyInstaller (_MEIPASS).
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Configuración global de la apariencia de la interfaz gráfica
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SettingsWindow(ctk.CTkToplevel):
    """
    Ventana secundaria para configurar y guardar las credenciales 
    de la API de Spotify y el usuario de TikTok.
    """
    def __init__(self, parent, update_callback):
        super().__init__(parent)
        self.geometry("400x320")
        self.title("Configuración de Credenciales")
        self.resizable(False, False)
        self.update_callback = update_callback

        # Carga segura del icono de la ventana
        try:
            icon_path = os.path.abspath(resource_path("logo.ico"))
            if os.path.exists(icon_path):
                self.wm_iconbitmap(icon_path)
        except Exception as e:
            print(f"Error cargando icono en settings: {e}")

        # Bloquea la interacción con la ventana principal hasta cerrar esta
        self.grab_set()

        # Componentes visuales del formulario de ajustes
        ctk.CTkLabel(self, text="Ajustes de API", font=("Arial", 16, "bold")).pack(pady=15)
        
        ctk.CTkLabel(self, text="Spotify Client ID:", font=("Arial", 11)).pack(anchor="w", padx=30)
        self.entry_client_id = ctk.CTkEntry(self, width=340, show="*")
        self.entry_client_id.pack(pady=2)

        ctk.CTkLabel(self, text="Spotify Client Secret:", font=("Arial", 11)).pack(anchor="w", padx=30)
        self.entry_client_secret = ctk.CTkEntry(self, width=340, show="*")
        self.entry_client_secret.pack(pady=2)

        ctk.CTkLabel(self, text="TikTok Username:", font=("Arial", 11)).pack(anchor="w", padx=30)
        self.entry_tiktok_user = ctk.CTkEntry(self, width=340)
        self.entry_tiktok_user.pack(pady=2)

        # Carga los valores actuales si ya existían previamente
        self.load_current_values()

        btn_save = ctk.CTkButton(self, text="Guardar Cambios", fg_color="blue", command=self.save_and_close)
        btn_save.pack(pady=15)

    def load_current_values(self):
        """Lee el archivo de configuración existente para rellenar los campos de texto."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.entry_client_id.insert(0, data.get("client_id", ""))
                    self.entry_client_secret.insert(0, data.get("client_secret", ""))
                    self.entry_tiktok_user.insert(0, data.get("tiktok_user", ""))
            except Exception:
                pass

    def save_and_close(self):
        """Almacena los datos ingresados en un archivo JSON local y cierra la ventana."""
        cid = self.entry_client_id.get().strip()
        csecret = self.entry_client_secret.get().strip()
        user = self.entry_tiktok_user.get().strip()

        data = {"client_id": cid, "client_secret": csecret, "tiktok_user": user}
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f)
            self.update_callback()
            self.destroy()
        except Exception as e:
            print(f"Error al guardar: {e}")

class BotApp(ctk.CTk):
    """
    Ventana principal de la aplicación que gestiona el estado del bot,
    los registros en tiempo real y la conexión con las plataformas.
    """
    def __init__(self):
        super().__init__()
        self.geometry("500x520")
        self.title("Bot Spotify & TikTok")
        
        # Carga del icono para la ventana principal
        try:
            icon_path = os.path.abspath(resource_path("logo.ico"))
            if os.path.exists(icon_path):
                self.wm_iconbitmap(icon_path)
        except Exception as e:
            print(f"Error cargando icono principal: {e}")

        self.resizable(False, False)
        self.is_running = False
        self.is_paused = False  # Bandera lógica para pausar la lectura de comentarios

        # Contenedor superior para el botón de ajustes
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=10, padx=20, fill="x")

        self.btn_settings = ctk.CTkButton(self.frame_top, text="⚙️ Settings", width=90, fg_color="gray30", hover_color="gray40", command=self.open_settings)
        self.btn_settings.pack(side="right")

        # Opciones adicionales (Casilla de verificación para habilitar el comando !skip)
        self.frame_options = ctk.CTkFrame(self)
        self.frame_options.pack(pady=10, padx=10, fill="x")

        self.skip_var = ctk.StringVar(value="off")
        self.checkbox_skip = ctk.CTkCheckBox(self.frame_options, text="Permitir comando !skip (saltar canción)", variable=self.skip_var, onvalue="on", offvalue="off")
        self.checkbox_skip.pack(pady=10, padx=10, anchor="w")

        # Panel de indicadores de estado visual (Spotify y TikTok)
        self.frame_status = ctk.CTkFrame(self)
        self.frame_status.pack(pady=5, padx=10, fill="x")

        self.lbl_spotify_status = ctk.CTkLabel(self.frame_status, text="🟢 Spotify: Listo", font=("Arial", 12, "bold"))
        self.lbl_spotify_status.pack(side="left", padx=25, pady=5)

        self.lbl_tiktok_status = ctk.CTkLabel(self.frame_status, text="🔴 TikTok: Offline", font=("Arial", 12, "bold"), text_color="orange")
        self.lbl_tiktok_status.pack(side="right", padx=25, pady=5)

        # Botón principal de control (Iniciar / Pausar / Reanudar)
        self.btn_toggle = ctk.CTkButton(self, text="Iniciar Bot", fg_color="green", hover_color="darkgreen", command=self.toggle_bot, height=35)
        self.btn_toggle.pack(pady=15)

        # Caja de texto para mostrar los registros (logs) del sistema en tiempo real
        self.log_box = ctk.CTkTextbox(self, width=460, height=200, font=("Consolas", 11))
        self.log_box.pack(pady=5, padx=10)
        self.log_box.insert("0.0", "Sistema preparado. Presiona 'Iniciar Bot'.\n")
        self.log_box.configure(state="disabled")

        self.check_initial_config()

    def check_initial_config(self):
        """Verifica si las credenciales ya existen al arrancar la aplicación."""
        if not os.path.exists(CONFIG_FILE):
            self.log_message("[Aviso] No hay credenciales configuradas. Da clic en '⚙️ Settings' para agregarlas.")
        else:
            self.log_message("[Sistema] Credenciales detectadas correctamente.")

    def open_settings(self):
        """Abre la ventana de configuración si el bot no está ejecutándose."""
        if self.is_running:
            self.log_message("[Aviso] Pausa o detén el bot antes de cambiar la configuración.")
            return
        SettingsWindow(self, self.on_settings_updated)

    def on_settings_updated(self):
        """Callback ejecutado al guardar cambios en la ventana de ajustes."""
        self.log_message("[Sistema] Credenciales actualizadas correctamente desde Settings.")

    def log_message(self, message):
        """Inserta mensajes de registro en la caja de texto de la UI de manera segura."""
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def toggle_bot(self):
        """Controla el flujo de arranque, pausa y reanudación del bot mediante hilos."""
        if not os.path.exists(CONFIG_FILE):
            self.log_message("[Error] Primero debes configurar tus credenciales en el botón '⚙️ Settings'.")
            return

        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                client_id = data.get("client_id", "").strip()
                client_secret = data.get("client_secret", "").strip()
                tiktok_user = data.get("tiktok_user", "").strip()
        except Exception:
            client_id, client_secret, tiktok_user = "", "", ""

        if not all([client_id, client_secret, tiktok_user]):
            self.log_message("[Error] Faltan datos en la configuración. Revisa '⚙️ Settings'.")
            return

        # Arranque inicial del bot en un hilo separado para no congelar la interfaz
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.btn_settings.configure(state="disabled")
            self.btn_toggle.configure(text="Pausar Bot", fg_color="orange", hover_color="darkorange")
            self.log_message("[Sistema] Iniciando conexión con plataformas...")

            self.bot_thread = threading.Thread(
                target=self.run_bot, 
                args=(client_id, client_secret, tiktok_user, self.skip_var.get()), 
                daemon=True
            )
            self.bot_thread.start()
        
        # Alterna entre estado de pausa y ejecución activa sin perder la conexión
        else:
            if not self.is_paused:
                self.is_paused = True
                self.btn_toggle.configure(text="Reanudar Bot", fg_color="green", hover_color="darkgreen")
                self.log_message("[Sistema] Bot pausado. No se atenderán comandos del chat temporalmente.")
            else:
                self.is_paused = False
                self.btn_toggle.configure(text="Pausar Bot", fg_color="orange", hover_color="darkorange")
                self.log_message("[Sistema] Bot reanudado. Escuchando el chat de nuevo.")

    def run_bot(self, cid, csecret, user, allow_skip):
        """Lógica principal de escucha de TikTok y control remoto de Spotify."""
        try:
            # Autenticación y conexión con la API de Spotify
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=cid, client_secret=csecret, 
                redirect_uri="http://127.0.0.1:8888/callback",
                scope="user-modify-playback-state user-read-playback-state",
                open_browser=False
            ))
            self.lbl_spotify_status.configure(text="🟢 Spotify: Conectado", text_color="lightgreen")
            self.log_message("[Spotify] Conectado exitosamente.")

        except Exception as e:
            self.lbl_spotify_status.configure(text="🔴 Spotify: Error", text_color="red")
            self.log_message(f"[Error de Spotify]: {e}")
            self.is_running = False
            self.is_paused = False
            self.btn_settings.configure(state="normal")
            self.btn_toggle.configure(text="Iniciar Bot", fg_color="green", hover_color="darkgreen")
            return

        # Inicialización del cliente de WebSockets para TikTok Live
        client = TikTokLiveClient(unique_id=user)

        @client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            """Escucha en tiempo real cada comentario enviado en el chat del directo."""
            if not self.is_running or self.is_paused:
                return
            
            comment = event.comment.strip()
            user_name = event.user.nickname
            comment_lower = comment.lower()

            # Procesamiento del comando !play para agregar canciones a la cola
            if comment_lower.startswith("!play "):
                search_query = comment[6:].strip()
                if search_query:
                    self.log_message(f"[Comando !play] {user_name}: '{search_query}'")
                    try:
                        results = sp.search(q=search_query, limit=1, type="track")
                        tracks = results.get("tracks", {}).get("items", [])

                        if tracks:
                            track_uri = tracks[0]["uri"]
                            track_name = tracks[0]["name"]
                            artist_name = tracks[0]["artists"][0]["name"]

                            sp.add_to_queue(uri=track_uri)
                            self.log_message(f"🎵 Añadida a cola: {track_name} - {artist_name}")
                        else:
                            self.log_message(f"⚠️ Sin resultados para: '{search_query}'")

                    except Exception as e:
                        self.log_message(f"[Error Spotify Play]: {e}")

            # Procesamiento opcional del comando !skip para saltar canciones
            elif allow_skip == "on" and comment_lower == "!skip":
                self.log_message(f"[Comando !skip] {user_name} solicitó saltar canción.")
                try:
                    sp.next_track()
                    self.log_message("⏭️ ¡Canción saltada correctamente!")
                except Exception as e:
                    self.log_message(f"[Error Spotify Skip]: {e}")

        try:
            self.log_message(f"Buscando el directo de @{user}...")
            self.lbl_tiktok_status.configure(text="🟢 TikTok: Conectado", text_color="lightgreen")
            client.run()
        except UserOfflineError:
            self.lbl_tiktok_status.configure(text="🔴 TikTok: Offline", text_color="orange")
            self.log_message(f"⚠️ El usuario @{user} está OFFLINE.")
            self.log_message(f"💡 Comienza tu live en TikTok y vuelve a reiniciar la app.")
        except Exception as e:
            self.lbl_tiktok_status.configure(text="🔴 TikTok: Error", text_color="red")
            self.log_message(f"[Error TikTok]: {e}")
        
        # Restablece los estados visuales y botones si la conexión finaliza
        self.is_running = False
        self.is_paused = False
        self.btn_settings.configure(state="normal")
        self.btn_toggle.configure(text="Iniciar Bot", fg_color="green", hover_color="darkgreen")
        self.lbl_tiktok_status.configure(text="🔴 TikTok: Offline", text_color="orange")

if __name__ == "__main__":
    app = BotApp()
    app.mainloop()