# BotAIChamuyo

Script de ejemplo que usa la API de OpenAI para generar respuestas a partir de dos archivos de contexto.

## Uso en consola

1. Instala dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Define la variable de entorno con tu API Key:

   ```bash
   export OPENAI_API_KEY="tu_api_key_aqui"
   ```

3. Edita `archivo1.txt` y `archivo2.txt` con el contexto deseado.

4. Ejecuta el script interactivo en consola:

   ```bash
   python script.py
   ```

## Bot de WhatsApp

Este proyecto incluye un bot básico que se conecta a WhatsApp utilizando la librería `pywhatsapp` y responde automáticamente a los mensajes recibidos mediante OpenAI.

1. Además de la clave de OpenAI, define las credenciales de WhatsApp:

   ```bash
   export WHATSAPP_LOGIN="numero_de_telefono"
   export WHATSAPP_PASSWORD="password_de_whatsapp"
   ```

2. Ejecuta el bot:

   ```bash
   python whatsapp_bot.py
   ```

## Docker

Puedes levantar el proyecto dentro de un contenedor Docker.

### Construir la imagen

```bash
docker build -t botai .
```

### Ejecutar el script interactivo

```bash
docker run --rm -it \
  -e OPENAI_API_KEY="tu_api_key_aqui" \
  -v $(pwd)/archivo1.txt:/app/archivo1.txt \
  -v $(pwd)/archivo2.txt:/app/archivo2.txt \
  botai
```

### Usar docker-compose

```bash
OPENAI_API_KEY=tu_api_key docker compose run script
```

Para iniciar el bot de WhatsApp:

```bash
OPENAI_API_KEY=tu_api_key WHATSAPP_LOGIN=numero WHATSAPP_PASSWORD=pass docker compose up whatsapp
```
