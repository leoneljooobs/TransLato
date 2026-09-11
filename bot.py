import os
import sys
import logging
from datetime import time
import pytz
from dotenv import load_dotenv

# Asegurar codificación utf-8 en la consola (especialmente en Windows)
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from database import (
    init_db,
    register_user,
    add_word,
    get_weekly_words,
    get_all_users,
    get_total_words_count,
)
from translator import translator

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configuración de logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Zona horaria para el scheduler (por defecto America/New_York o America/Mexico_City / local)
TIMEZONE_STR = os.getenv("BOT_TIMEZONE", "America/New_York")
try:
    BOT_TIMEZONE = pytz.timezone(TIMEZONE_STR)
except Exception:
    BOT_TIMEZONE = pytz.UTC


def format_words_summary(words: list, title: str = "📚 Resumen Semanal de Vocabulario") -> list[str]:
    """Formatea la lista de palabras en uno o varios mensajes respetando el límite de Telegram."""
    if not words:
        return ["No tienes palabras registradas en los últimos 7 días. ¡Envíame palabras en inglés para empezar a practicar! 🚀"]

    lines = [f"*{title}*\nTotal: *{len(words)} palabras*\n"]
    for i, item in enumerate(words, 1):
        orig = item["original_text"]
        trans = item["translated_text"]
        lines.append(f"{i}. *{orig}* ➔ _{trans}_")

    # Dividir en mensajes de máximo ~3800 caracteres para evitar errores de Telegram
    messages = []
    current_msg = ""
    for line in lines:
        if len(current_msg) + len(line) + 1 > 3800:
            messages.append(current_msg.strip())
            current_msg = ""
        current_msg += line + "\n"
    if current_msg.strip():
        messages.append(current_msg.strip())

    return messages


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando /start."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    register_user(user.id, chat_id, user.username)

    mensaje = (
        f"👋 ¡Hola, *{user.first_name}*!\n\n"
        "Soy tu bot personal de **inglés y vocabulario** 🇬🇧 ➡️ 🇪🇸.\n\n"
        "✨ **¿Cómo funciono?**\n"
        "1. Escríbeme cualquier palabra o frase en inglés.\n"
        "2. Te la traduciré al instante y la guardaré en tu libreta semanal.\n"
        "3. **Cada fin de semana (Domingos a las 20:00)** te enviaré un resumen completo de todas las palabras aprendidas para que las repases.\n\n"
        "📌 **Comandos útiles:**\n"
        "• `/semana` o `/resumen` - Ver tus palabras de esta semana ahora mismo.\n"
        "• `/stats` - Ver estadísticas de tu aprendizaje.\n"
        "• `/ayuda` - Ver instrucciones y soporte.\n\n"
        "¡Empieza ahora! Escribe una palabra en inglés, por ejemplo: `knowledge`"
    )
    await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando /ayuda."""
    mensaje = (
        "💡 **Guía de Uso del Bot:**\n\n"
        "• **Traducir:** Simplemente envía una palabra o frase en inglés (ej: `apple`, `break a leg`).\n"
        "• `/semana` o `/resumen`: Consulta el listado acumulado de los últimos 7 días.\n"
        "• `/stats`: Consulta el número total de palabras registradas.\n"
        "• **Resumen automático:** Se envía todos los domingos por la noche de forma automática."
    )
    await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando /stats."""
    user_id = update.effective_user.id
    total = get_total_words_count(user_id)
    weekly = len(get_weekly_words(user_id, days=7))

    mensaje = (
        "📊 **Tus Estadísticas de Aprendizaje:**\n\n"
        f"• Palabras esta semana: *{weekly}*\n"
        f"• Total acumulado histórico: *{total}*\n\n"
        "¡Sigue sumando vocabulario cada día! 💪"
    )
    await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)


async def weekly_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando manual /semana o /resumen."""
    user_id = update.effective_user.id
    words = get_weekly_words(user_id, days=7)
    chunks = format_words_summary(words, title="📖 Tu Vocabulario de los Últimos 7 Días")
    for chunk in chunks:
        await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Traduce el mensaje recibido y lo guarda en la base de datos."""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    user = update.effective_user
    chat_id = update.effective_chat.id

    try:
        # Traducir el texto
        translation = translator.translate(text)

        # Guardar en base de datos
        add_word(user.id, chat_id, text, translation, user.username)

        # Responder al usuario
        respuesta = (
            f"🇬🇧 *Inglés:* `{text}`\n"
            f"🇪🇸 *Español:* *{translation}*\n\n"
            "✅ _Guardado para tu resumen del fin de semana_"
        )
        await update.message.reply_text(respuesta, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        await update.message.reply_text(
            "⚠️ Ocurrió un error al traducir la palabra. Por favor intenta de nuevo en unos momentos."
        )


async def send_weekend_summary_job(context: ContextTypes.DEFAULT_TYPE):
    """Tarea programada que envía el resumen semanal a todos los usuarios cada domingo."""
    logger.info("Ejecutando tarea programada: Resumen semanal de vocabulario...")
    users = get_all_users()
    for u in users:
        user_id = u["user_id"]
        chat_id = u["chat_id"]
        words = get_weekly_words(user_id, days=7)
        if words:
            chunks = format_words_summary(words, title="🎉 ¡Llegó el Fin de Semana! Tu Resumen Semanal")
            for chunk in chunks:
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=chunk,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                except Exception as err:
                    logger.error(f"Error enviando resumen a {chat_id}: {err}")


from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Manejador HTTP simple para responder a los chequeos de Render/Cloud."""
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is running OK")

    def log_message(self, format, *args):
        pass  # Silenciar logs recurrentes del health check

def start_health_server(port: int):
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info(f"Servidor HTTP de salud activo en puerto {port}")
    server.serve_forever()

def main():
    """Punto de entrada para iniciar el bot."""
    if not TOKEN or "TU_TOKEN" in TOKEN or len(TOKEN.strip()) < 10:
        print("\n" + "=" * 60)
        print("AVISO: TELEGRAM_BOT_TOKEN no configurado.")
        print("Por favor, abre el archivo .env y pega el token de tu bot de @BotFather.")
        print("Ejemplo: TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRstuVWXyz")
        print("=" * 60 + "\n")
        return

    # Iniciar servidor HTTP en segundo plano si la plataforma define $PORT (Render Web Service)
    port_env = os.getenv("PORT")
    if port_env:
        try:
            port_num = int(port_env)
            t = threading.Thread(target=start_health_server, args=(port_num,), daemon=True)
            t.start()
        except Exception as e:
            logger.error(f"Error iniciando servidor HTTP en puerto {port_env}: {e}")

    # Inicializar Base de Datos
    init_db()

    # Construir la aplicación del bot
    application = Application.builder().token(TOKEN).build()

    # Registrar comandos
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ayuda", help_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("semana", weekly_command))
    application.add_handler(CommandHandler("resumen", weekly_command))
    application.add_handler(CommandHandler("stats", stats_command))

    # Registrar manejador de mensajes de texto (no comandos)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Configurar tarea programada semanal: Domingos a las 20:00 (8:00 PM)
    job_queue = application.job_queue
    if job_queue:
        # 6 = Domingo (Monday = 0, Sunday = 6)
        scheduled_time = time(hour=20, minute=0, tzinfo=BOT_TIMEZONE)
        job_queue.run_daily(
            send_weekend_summary_job,
            time=scheduled_time,
            days=(6,),  # Domingo
            name="weekly_summary_job"
        )
        logger.info(f"Programador configurado para domingos a las 20:00 ({TIMEZONE_STR})")
    else:
        logger.warning("JobQueue no está disponible. Revisa la instalación de python-telegram-bot[job-queue]")

    # Iniciar el bot en modo polling
    print("🤖 El bot está en ejecución y escuchando mensajes...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

