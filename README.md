# 🤖 Bot de Telegram: Traductor y Resumen Semanal de Vocabulario

Este bot te permite aprender y recordar vocabulario en inglés día a día:
1. **Traducción instantánea**: Le envías cualquier palabra o frase en inglés y te responderá con su traducción al instante.
2. **Registro automático**: Cada palabra consultada se guarda automáticamente en una base de datos local SQLite.
3. **Resumen semanal automático**: Cada domingo a las 20:00 (o cuando tú quieras usando el comando `/semana`), el bot te enviará un resumen organizado de todo lo que practicaste en la semana para repasar.

---

## 🚀 Pasos para Configurar y Ejecutar

### 1. Obtener el Token de Telegram (Gratis en 1 minuto)
1. Abre Telegram y busca a **[@BotFather](https://t.me/BotFather)**.
2. Envía el comando `/newbot`.
3. Sigue las instrucciones:
   - Asígnale un nombre a tu bot (por ejemplo: `Mi Traductor Ingles`).
   - Asígnale un usuario único que termine en `bot` (por ejemplo: `MiTraductorIngles_bot`).
4. BotFather te entregará un **Token de acceso** (algo como `123456789:ABCdefGhIJKlmNoPQRstuVWXyz`). Copia este token.

### 2. Configurar el Token en el Proyecto
Abre el archivo `.env` en esta carpeta (`C:\Users\lenovo\Desktop\chatbot\.env`) y pega tu token:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRstuVWXyz
BOT_TIMEZONE=America/New_York
```

*(Puedes cambiar la zona horaria según tu país, por ejemplo `America/Mexico_City`, `America/Bogota`, `America/Santiago`, `Europe/Madrid`, etc.)*

### 3. Instalar Dependencias
Abre una terminal en esta carpeta y ejecuta:
```bash
pip install -r requirements.txt
```

### 4. Iniciar el Bot
Ejecuta:
```bash
python bot.py
```

¡Listo! Ve a tu bot en Telegram, presiona **Iniciar** (o envía `/start`) y empieza a enviarle palabras en inglés.

---

## 📱 Comandos Disponibles en Telegram

| Comando | Descripción |
| :--- | :--- |
| `/start` | Inicia el bot y muestra el mensaje de bienvenida y guía. |
| `/semana` o `/resumen` | Muestra en cualquier momento la lista de palabras aprendidas en los últimos 7 días. |
| `/stats` | Muestra el conteo de palabras aprendidas en la semana y el total acumulado. |
| `/ayuda` | Muestra información de ayuda y comandos. |

---

## 🛠️ Estructura del Proyecto

- `bot.py`: Lógica principal del bot de Telegram, manejadores de mensajes y scheduler semanal.
- `database.py`: Gestión de base de datos SQLite (`words.db`) para guardar usuarios y palabras.
- `translator.py`: Servicio de traducción rápida inglés-español con `deep-translator`.
- `Dockerfile`: Configuración del contenedor Docker para producción o Render.
- `docker-compose.yml`: Configuración para levantar el contenedor localmente con volúmenes persistentes.
- `render.yaml`: Manifiesto para despliegue automatizado en Render.
- `test_core.py`: Pruebas automatizadas de traducción y persistencia.
- `requirements.txt`: Dependencias del proyecto.
- `.env`: Archivo de configuración para tu token de Telegram y zona horaria.

---

## 🐳 Despliegue Local con Docker

Si tienes Docker instalado en tu computadora, puedes iniciar el bot en un contenedor ejecutando:

```bash
docker compose up -d --build
```

Para ver los logs del bot:
```bash
docker compose logs -f
```

Para detenerlo:
```bash
docker compose down
```

---

## ☁️ Despliegue Gratuito en Render.com (24/7)

Para que el bot funcione 24/7 sin necesidad de tener tu computadora encendida:

### Paso 1: Subir el proyecto a GitHub
1. Crea un repositorio en [GitHub](https://github.com/new) (puede ser privado o público).
2. En la terminal de esta carpeta (`C:\Users\lenovo\Desktop\chatbot`), inicializa Git y sube los archivos:
   ```bash
   git init
   git add .
   git commit -m "Initial commit bot telegram"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git push -u origin main
   ```
   *(El archivo `.gitignore` ya está configurado para que tu token `.env` NO se suba a GitHub por seguridad).*

### Paso 2: Conectar con Render
1. Ve a [dashboard.render.com](https://dashboard.render.com/) e inicia sesión (puedes entrar con tu cuenta de GitHub).
2. Haz clic en **New +** y selecciona **Web Service**.
3. Selecciona tu repositorio de GitHub recién subido.
4. Render detectará automáticamente el **Dockerfile**:
   - **Language / Runtime:** Docker
   - **Instance Type:** Free
5. En la sección **Environment Variables**, añade:
   - `TELEGRAM_BOT_TOKEN`: Pega aquí tu token de BotFather (`8818467089:...`).
   - `BOT_TIMEZONE`: Tu zona horaria (ej: `America/New_York` o `America/Mexico_City`).
6. Haz clic en **Deploy Web Service**.

¡Listo! Render compilará el contenedor Docker y tu bot quedará funcionando 24/7 en la nube.


