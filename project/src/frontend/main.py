import requests
"""
El código define una aplicación de Streamlit que interactúa con un servicio backend para procesar la entrada del usuario, mostrar mensajes 
de chat y mostrar resultados de búsqueda con botones clicables.
query: El parámetro query es una cadena de texto que representa la consulta de búsqueda que se enviará al backend para su procesamiento. 
Se utiliza para recuperar información o datos relevantes basados en la entrada o pregunta del usuario. En el fragmento de código proporcionado, 
el parámetro query se utiliza para construir la URL para la consulta.

query: str
"""        
import json
import time
import streamlit as st
import sseclient  # sseclient-py


def backend_call(query: str):
    """
La función `backend_call` realiza una solicitud HTTP GET en streaming a una URL especificada y genera eventos desde la respuesta del servidor de 
forma indefinida.
- `query`: La función `backend_call` toma un parámetro `query`, que es una cadena de texto que representa la consulta de búsqueda que se enviará 
al servidor backend para su procesamiento. La función luego construye una URL con el parámetro de consulta y realiza una solicitud GET en 
streaming al servidor. Utiliza Eventos Enviados por el Servidor (SSE).
- `type query`: str
    """
    url = f"http://orchestrator/streamingSearch?query={query}"
    stream_response = requests.get(url, stream=True)
    client = sseclient.SSEClient(stream_response)  # type: ignore

    # Loop forever (while connection "open")
    for event in client.events():
        yield event
        
from requests.exceptions import ChunkedEncodingError
import time

from sseclient import SSEClient

class CustomSSEClient(SSEClient):
    def events(self):
        data = b""  # Asegúrate de que data sea de tipo bytes
        for chunk in self._read():
            if isinstance(chunk, str):
                chunk = chunk.encode('utf-8')  # Convierte chunk a bytes si es una cadena
            elif isinstance(chunk, bytes):
                pass  # Ya es bytes, no se necesita conversión
            else:
                continue  # Maneja otros tipos de datos si es necesario

            data += chunk
            for line in data.decode(self._char_enc).splitlines():
                if line.startswith(':'):
                    continue
                if not line:
                    yield event
                    event = self._event_class()
                    continue
                data = line.split(':', 1)
                field = data[0]
                if len(data) > 1:
                    value = data[1].lstrip()
                else:
                    value = ''
                if field == 'data':
                    event.data += value + '\n'
                elif field == 'event':
                    event.event = value
                elif field == 'id':
                    event.id = value
                elif field == 'retry':
                    try:
                        event.retry = int(value)
                    except ValueError:
                        pass
        if event.data:
            yield event


from requests.exceptions import RequestException

def backend_call(prompt):
    max_retries = 5
    retry_delay = 2
    timeout = 10

    for attempt in range(max_retries):
        try:
            url = f"http://orchestrator:80/streamingSearch?query={prompt}"
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()
            client = CustomSSEClient(response)
            for event in client.events():
                yield event
            break
        except RequestException as e:
            print(f"Intento {attempt + 1} fallido: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print("No se pudo establecer conexión con el backend después de múltiples intentos.")
                raise



def display_chat_messages():
    """
    La función `display_chat_messages` muestra los mensajes del chat desde el historial cuando la aplicación se vuelve a ejecutar.
    """
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def process_user_input(prompt):
    """
La función `process_user_input` añade la entrada del usuario a una lista en el estado de la sesión y la muestra en un contenedor de mensajes del 
chat.
- `prompt`: La función `process_user_input` esta diseñada para procesar la entrada del usuario en una aplicación de chat. Toma un `prompt` 
como entrada, agrega el mensaje del usuario a una lista en el estado de la sesión, y luego muestra el mensaje del usuario en un contenedor de 
mensajes del chat usando Streamlit.
    """
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)


def process_backend_response(prompt):
    """
La función `process_backend_response` procesa las respuestas del backend mostrándolas en columnas con botones y actualizando la respuesta completa.
- `prompt`: El parámetro `prompt` es la entrada o consulta que se envía al backend para su procesamiento. Puede ser una pregunta, un comando, o 
cualquier otra forma de entrada del usuario que el sistema backend necesite manejar y responder.
    """
    full_response = ""
    columns = st.columns(2)
    button_count = 0
    button_placeholders, message_placeholder = [], None
    with st.spinner("Thinking..."):
        for chunk in backend_call(prompt):
            button_count, button_placeholders = display_backend_response(
                chunk, button_count, columns, button_placeholders
            )
            full_response, message_placeholder = process_chunk_event(
                chunk, full_response, message_placeholder
            )

    st.session_state.messages.append({"role": "assistant", "content": full_response})


def display_backend_response(chunk, button_count, columns, button_placeholders):
    """
La función `display_backend_response` procesa resultados de búsqueda y crea botones con enlaces acortados.

- `chunk`: El parámetro `chunk` parece ser un objeto o estructura de datos que contiene información relacionada con un evento, posiblemente 
vinculado a una operación de búsqueda. La función `display_backend_response` procesa este fragmento de datos y realiza ciertas acciones basadas 
en el tipo de evento. En este caso, parece estar manejando un
- `button_count`: El parámetro `button_count` se utiliza para llevar un registro de la cantidad de botones creados en la función `display_backend_response`. 
Se incrementa cada vez que se crea un nuevo botón, asegurando que cada botón tenga un identificador único
- `columns`: El parámetro `columns` parece ser usado en la función `display_backend_response` como un argumento. Probablemente se utiliza para 
determinar el número de columnas en una visualización o diseño. La implementación específica de cómo se usa `columns` dentro de la función no se 
proporciona en el fragmento compartido
- `button_placeholders`: El parámetro `button_placeholders` es una lista que almacena los marcadores de posición de los botones. Estos marcadores 
de posición se crean dinámicamente en la función `display_backend_response` para cada elemento en los resultados de búsqueda. A cada marcador se 
le asigna una etiqueta basada en el enlace del ítem y una clave única. Los marcadores de posición de los botones son entonces
- `return`: La función `display_backend_response` devuelve el `button_count` actualizado y los `button_placeholders` después de procesar los datos
 `chunk` en respuesta a un evento de "búsqueda".
    """
    if chunk.event == "search":
        for item in json.loads(chunk.data).get("items"):
            button_placeholder = assign_button_placeholder(columns, button_placeholders)
            button_placeholder.button(
                label=item.get("link")[8:42] + "...", key=button_count
            )
            button_count += 1
            button_placeholders.append(button_placeholder)
            time.sleep(0.05)
    return button_count, button_placeholders


def assign_button_placeholder(columns, button_placeholders):
    """
La función `assign_button_placeholder` determina qué columna vaciar según la paridad del número de marcadores de posición de los botones 
proporcionados.

- `columns`: El parámetro `columns` es una lista de columnas en un diseño de interfaz de usuario. Cada columna puede contener diferentes elementos
como botones, campos de texto u otros componentes de la interfaz de usuario.
- `button_placeholders`: El parámetro `button_placeholders` es una lista que contiene los marcadores de posición para botones en una interfaz de
usuario. Cada marcador de posición representa un botón que se puede crear dinámicamente
- `return`: Devuelve `columns[0].empty()` o `columns[1].empty()` según si la longitud de `button_placeholders` es par o impar.
    """
    return (
        columns[0].empty() if len(button_placeholders) % 2 == 0 else columns[1].empty()
    )


def process_chunk_event(chunk, full_response, message_placeholder):
    """
    La función `process_chunk_event` procesa un evento de fragmento actualizando una respuesta completa y mostrándola con un marcador de posición 
    de mensaje en formato markdown.

- `chunk`: El parámetro `chunk` parece representar una parte o sección de datos que se está procesando. Probablemente contiene información 
relacionada con un evento, como un evento de token en este caso.
- `full_response`: El parámetro `full_response` es una cadena que almacena los datos de respuesta completa acumulados a partir del procesamiento 
de fragmentos individuales.
- `message_placeholder`: El parámetro `message_placeholder` es un elemento marcador de posición que puede usarse para mostrar mensajes o contenido
 en una aplicación de Streamlit. En la función proporcionada `process_chunk_event`, si `message_placeholder` no se proporciona (es decir, si es 
 `None`), se crea un nuevo marcador de posición vacío usando
- `return`: La función `process_chunk_event` devuelve dos valores: `full_response` y `message_placeholder`.
    """
    if chunk.event == "token":
        if not message_placeholder:
            message_placeholder = st.empty()
        full_response += chunk.data
        message_placeholder.markdown(full_response + "▌")
    return full_response, message_placeholder


# El fragmento de código es un script de Python que utiliza Streamlit, una biblioteca popular para crear aplicaciones web con Python. 
# Desglosemos las líneas específicas que mencionaste:
st.title("InternetWhisper")
# Initialize chat history
st.session_state.messages = st.session_state.get("messages", [])

display_chat_messages()

#Aquí tienes la traducción:

# El fragmento de código está utilizando una característica en Python llamada el "operador walrus" (`:=`) junto con una instrucción if para 
# manejar la entrada del usuario en una aplicación de chat construida con Streamlit.
# Accept user input
if prompt := st.chat_input("Ask me a question..."):
    process_user_input(prompt)
    process_backend_response(prompt)
