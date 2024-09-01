# InternetWhisper: Chatbot conversacional de IA con acceso a Internet

## Descripción del proyecto

Basado en You.com y Google's Bard, este proyecto es un chatbot conversacional de inteligencia artificial generativa que puede acceder a Internet. Está diseñado para proporcionar información en tiempo real y entablar conversaciones con los usuarios. Para mejorar su rendimiento, el chatbot utiliza una base de datos vectorial Redis (caché Redis Vector DB) para almacenar la información recuperada previamente, lo que reduce la necesidad de consultar Internet los mismos datos repetidamente. También aprovecha la API de búsqueda de Google para consultar sitios web.

![ezgif-5-4b30015e27](https://github.com/santiagomorillosegovia/InternetWhisper/assets/28943730/26840b24-92d3-4ddf-bbd1-82cc6b992c7f)

## Explicacion Técnica

Es un proyecto que utiliza FastAPI para crear una aplicación web que interactúa con la API de OpenAI, específicamente con el modelo GPT-3.5 Turbo, para generar respuestas en tiempo real a través de una interfaz de eventos de servidor enviados (SSE). A continuación, se detalla la funcionalidad de cada componente basado en los fragmentos de código proporcionados:

- FastAPI: Se utiliza FastAPI como framework para crear una API web rápida y eficiente. FastAPI facilita la creación de endpoints y la gestión de solicitudes y respuestas HTTP.

- EventSourceResponse: Se utiliza para enviar eventos en tiempo real al cliente. Esto permite una comunicación bidireccional entre el servidor y el cliente, donde el servidor puede enviar actualizaciones sin que el cliente las solicite explícitamente.

- Logger: Se utiliza para registrar eventos y mensajes importantes durante la ejecución del código. Esto es útil para el seguimiento y la depuración.

- OpenAI: Se importa la biblioteca de OpenAI para interactuar con la API de GPT-3.5 Turbo. Esto permite generar respuestas automáticas a los mensajes de los usuarios.

- Retriever y sus submódulos: Estos componentes estan relacionados con la recuperación y el procesamiento de información. Incluyen la búsqueda de información (GoogleAPI), el almacenamiento en caché de vectores (RedisVectorCache), el raspado de datos (ScraperLocal y ScraperRemote), la generación de incrustaciones de texto (OpenAIEmbeddings y RemoteEmbeddings) y la división de texto (LangChainSplitter).

- stream_chat: Esta función genera respuestas en tiempo real utilizando la API de OpenAI. Se comunica con el modelo GPT-3.5 Turbo, enviando mensajes del usuario y recibiendo respuestas que luego se transmiten al cliente.

- Dockerfile: Se proporciona un Dockerfile para contenerizar la aplicación, lo que facilita su despliegue y escalabilidad. Se basa en una imagen de Python y se instalan las dependencias necesarias, incluyendo Spacy para el procesamiento de lenguaje natural.

- requirements.txt: Este archivo lista todas las bibliotecas y sus versiones específicas que son necesarias para ejecutar la aplicación. Esto asegura que el entorno de ejecución sea consistente.

## Primeros pasos

Sigue estos pasos para ejecutar el chatbot localmente en tu máquina:

1. **Configurar variables de entorno**:

   - Cree un archivo `.env` copiando el archivo `.env.example` proporcionado. Este archivo debe contener las siguientes variables de entorno:
     - `HEADER_ACCEPT_ENCODING`: Ajústala a "gzip".
     - `HEADER_USER_AGENT`: Utilice una cadena de agente de usuario, por ejemplo, "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/116.0.0.0 Safari/537.36 (gzip)".
     - `GOOGLE_API_HOST`: Establece el host de la API de Google en "https://www.googleapis.com/customsearch/v1?".
     - `GOOGLE_FIELDS`: Define los campos que deseas recuperar de Google. Ejemplo: "items(title, displayLink, link, snippet,pagemap/cse_thumbnail)".
     - `GOOGLE_API_KEY`: Obtener una clave API de Google de [Google Custom Search](https://developers.google.com/custom-search/v1/overview).
     - `GOOGLE_CX`: Puedes obtener tu ID de motor de búsqueda personalizado (CX) en la misma página de búsqueda personalizada de Google.
     - `OPENAI_API_KEY`: Obtén una clave API de [OpenAI](https://openai.com/blog/openai-api).

2. **Construir y ejecutar la aplicación**:

   - Abre tu terminal y navega al directorio del proyecto.
   - Ejecuta los siguientes comandos para compilar e iniciar la aplicación utilizando Docker Compose:

   ```bash
   docker-compose build
   docker-compose up
   ```

3. **Elige tu clase de scraper**:

   El proyecto incluye dos clases de scraper:

   - `ScraperLocal`: Utiliza aiohttp para el web scraping (por defecto).
   - `ScraperRemote`: Utiliza Playwright en un contenedor replicado separado para un renderizado de JavaScript más complejo.

   Para cambiar entre las clases de scraper, modifica el archivo `orchestrator/main.py` y descomenta los servicios scraper y lb-scraper apropiados en `docker-compose.yml`.

4. - `OpenAIEmbeddings`: La opción por defecto, usando los embeddings de OpenAI.

5. **Accede al Chatbot**:

   Después de ejecutar la aplicación, abre tu navegador web y navega a [http://localhost:8501/](http://localhost:8501/) para interactuar con el chatbot.

Siéntete libre de explorar y modificar este chatbot conversacional de IA para tu caso de uso específico. ¡Disfruta chateando con tu nuevo compañero de IA!

Traducción realizada con la versión gratuita del traductor DeepL.com

## Definicion OpenAPI

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "FastAPI",
    "version": "0.1.0"
  },
  "paths": {
    "/streamingSearch": {
      "get": {
        "summary": "Main",
        "operationId": "main_streamingSearch_get",
        "parameters": [
          {
            "name": "query",
            "in": "query",
            "required": true,
            "schema": {
              "title": "Query",
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "text/event-stream": {
                "schema": {
                  "title": "Response",
                  "type": "string"
                }
              }
            }
          }
        }
      }
    }
  }
}
```
