# InternetWhisper: Chatbot Conversacional de IA con Acceso a Internet

## Descripción del Proyecto

InternetWhisper es un innovador chatbot conversacional de inteligencia artificial generativa con la capacidad única de acceder a Internet en tiempo real. Inspirado en You.com y Google's Bard, este proyecto ofrece una experiencia de conversación enriquecida con información actualizada del mundo online.

Características principales:

- Acceso a información en tiempo real de Internet
- Conversaciones fluidas y contextuales
- Almacenamiento eficiente de información en una base de datos vectorial Redis
- Integración con la API de búsqueda de Google para consultas web precisas

El valor agregado de InternetWhisper radica en su capacidad para combinar la potencia de la IA conversacional con el vasto conocimiento disponible en Internet, proporcionando respuestas informadas y actualizadas a los usuarios.

## Explicación Técnica

InternetWhisper utiliza una arquitectura moderna y eficiente:

- **FastAPI**: Framework web para crear API rápidas y eficientes.
- **OpenAI GPT-3.5 Turbo**: Motor de IA para generar respuestas conversacionales.
- **Redis Vector DB**: Caché para almacenar y recuperar rápidamente información previa.
- **Google Search API**: Para realizar búsquedas web en tiempo real.
- **Embeddings**: Utiliza OpenAIEmbeddings para procesar y vectorizar texto.
- **Web Scraping**: Implementa ScraperLocal (aiohttp) y ScraperRemote (Playwright) para extraer información de sitios web.
- **Text Splitting**: Emplea LangChainSplitter para dividir textos largos en fragmentos manejables.

La aplicación integra estas tecnologías para procesar las consultas de los usuarios, buscar información relevante en Internet, almacenar datos en caché para futuras consultas y generar respuestas coherentes y contextuales.

## Pasos para Configurar Variables de Entorno

1. Copia el archivo `.env.example` y renómbralo a `.env`.
2. Configura las siguientes variables en el archivo `.env`:

   - `HEADER_ACCEPT_ENCODING`: Establece a "gzip"
   - `HEADER_USER_AGENT`: Usa un string de user agent válido
   - `GOOGLE_API_HOST`: URL base de la API de Google
   - `GOOGLE_FIELDS`: Campos a recuperar de Google
   - `GOOGLE_API_KEY`: Tu clave API de Google Custom Search
   - `GOOGLE_CX`: ID de tu motor de búsqueda personalizado
   - `OPENAI_API_KEY`: Tu clave API de OpenAI

## Pasos para Correr la Aplicación Localmente

1. Asegúrate de tener Docker y Docker Compose instalados en tu sistema.
2. Navega al directorio del proyecto en tu terminal.
3. Ejecuta los siguientes comandos:

   ```bash
   docker-compose build
   docker-compose up
   ```

## Definición OpenAPI de la API

la API en este proyecto es FastAPI.
El proyecto utiliza FastAPI como framework para crear esta API web rápida y eficiente, facilitando la creación de endpoints y la gestión de solicitudes y respuestas HTTP.

La definición OpenAPI muestra un endpoint /streamingSearch que utiliza el método GET. Este endpoint acepta un parámetro de consulta llamado "query" y devuelve una respuesta en formato de flujo de eventos (text/event-stream).
La API está diseñada para manejar solicitudes de búsqueda en tiempo real y proporcionar respuestas utilizando Server-Sent Events (SSE). Esto permite una comunicación en tiempo real entre el cliente y el servidor, donde el servidor puede enviar actualizaciones continuas al cliente sin necesidad de solicitudes adicionales.

La documentación OpenAPI de InternetWhisper se genera automáticamente gracias a FastAPI. Para acceder a ella:

1. Inicia la aplicación siguiendo los pasos mencionados anteriormente.
2. Abre tu navegador y visita `http://localhost:8000/docs` para ver la interfaz Swagger UI.
3. Alternativamente, puedes acceder a `http://localhost:8000/redoc` para una versión más detallada usando ReDoc.

Esta documentación es crucial ya que:

- Proporciona una visión general de todos los endpoints disponibles.
- Permite probar la API directamente desde el navegador.
- Facilita la comprensión de los parámetros de entrada y los formatos de respuesta.
- Ayuda a los desarrolladores a integrar InternetWhisper en sus propias aplicaciones.

La definición OpenAPI incluye detalles sobre el endpoint `/streamingSearch`, que es el corazón de nuestra aplicación. Utiliza esta documentación para entender cómo realizar consultas y qué esperar como respuesta.
