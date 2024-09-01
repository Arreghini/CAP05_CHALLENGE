
from abc import ABC, abstractmethod
import hashlib
import json
import numpy as np
import pandas as pd
import redis
from redis.commands.search.field import (
    TextField,
    VectorField,
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from models.document import Document

VECTOR_DIMENSION = 1536

# La clase VectorDbCache define métodos abstractos para encontrar documentos similares y para escribir documentos en una caché de base de datos 
# vectorial.
class VectorDbCache(ABC):
    @abstractmethod
    async def find_similar(self, vector: list[float], k=10) -> list[Document]:
        pass

    @abstractmethod
    async def write(self, documents: list[Document]):
        pass


SHA256 = hashlib.sha256()


# La clase RedisVectorCache es una subclase de VectorDbCache que utiliza Redis para la caché e implementa un método para encontrar documentos 
# similares basados en vectores de entrada.
class RedisVectorCache(VectorDbCache):
    _pool = None

    def __init__(self, host, port) -> None:
        if RedisVectorCache._pool is None:
            RedisVectorCache._pool = redis.ConnectionPool(host=host, port=port)

        self.client = redis.Redis(
            connection_pool=RedisVectorCache._pool, decode_responses=True
        )

    async def find_similar(self, vector: list[float], k=10) -> list[Document]:
        chunks = (
            self.client.ft("idx:chunks_vss")
            .search(
                Query(f"(*)=>[KNN {k} @vector $query_vector AS vector_score]")
                .sort_by("vector_score")
                .return_fields("vector_score", "text", "url", "vector")
                .dialect(2),
                {"query_vector": np.array(vector, dtype=np.float32).tobytes()},
            )
            .docs  # type: ignore
        )
        documents = map(
            lambda doc: Document(
                url=doc.url,
                text=doc.text,
                vector=json.loads(doc.vector),
                similarity=1 - float(doc.vector_score),
            ),
            chunks,
        )

        return list(documents)

    async def get_insertables(self, documents: list[Document]) -> list[Document]:
        """
    Esta función toma una lista de documentos, encuentra documentos similares y devuelve una lista de documentos que se consideran insertables
    basándose en un umbral de similitud.
    documents: El parámetro documents es una lista de objetos Document que se pasan al método get_insertables. Cada objeto Document probablemente 
    contiene información o datos que necesitan ser procesados dentro del método.
    type documents: list[Document]
    return: El método get_insertables devuelve una lista de objetos Document que se consideran insertables según ciertas condiciones.
        """
        insertables = []
        for document in documents:
            results = await self.find_similar(document.vector, k=1)
            if not results:
                insertables.append(document)
            elif results[0].similarity < 0.97:
                insertables.append(document)
        return insertables

    async def write(self, documents: list[Document]):
        """
    La función escribe una lista de documentos en una base de datos Redis utilizando una operación de pipeline específica.
    documents: El método write parece estar escribiendo documentos en una base de datos Redis utilizando un pipeline para mejorar el rendimiento. 
    Calcula un hash SHA256 para el texto de cada documento, establece una clave en Redis con el ID del fragmento, y luego almacena los datos del 
    documento en formato JSON con un tiempo de expiración de 360.
    type documents: list[Document]
        """
        documents = await self.get_insertables(documents)
        pipeline = self.client.pipeline()
        for document in documents:
            SHA256.update(document.text.encode("utf-8"))
            chunk_id = SHA256.hexdigest()
            redis_key = f"chunks:{chunk_id}"
            document.similarity = -1
            pipeline.json().set(redis_key, "$", document.model_dump())
            pipeline.expire(redis_key, 3600)

        pipeline.execute()

    def init_test(self):
        """
       Esta función lee datos de un archivo pickle, los procesa, calcula un hash SHA256 y almacena los datos en Redis utilizando un pipeline.
        """
        df = pd.read_pickle("mocks/database_pickle")
        df["vector"] = df["vector"].apply(lambda x: x.tolist()[0])
        chunks = df.to_dict("records")

        pipeline = self.client.pipeline()
        for chunk in chunks:
            SHA256.update(chunk["text"].encode("utf-8"))
            chunk_id = SHA256.hexdigest()
            redis_key = f"chunks:{chunk_id}"
            pipeline.json().set(redis_key, "$", chunk)
        pipeline.execute()

    def init_index(self, vector_dimension):
        """
    La función init_index inicializa un índice con un esquema y una definición específicos para un servicio de búsqueda vectorial.
    vector_dimension: El parámetro vector_dimension en el método init_index se utiliza para especificar la dimensionalidad del campo vectorial 
    que se creará en el índice. Esta dimensionalidad determina la cantidad de componentes en el campo vectorial. En el fragmento de código 
    proporcionado, el campo vectorial se define con una dimensión especificada.
        """
        schema = (
            TextField("$.text", no_stem=True, as_name="text"),
            TextField("$.url", no_stem=True, as_name="url"),
            VectorField(
                "$.vector",
                "FLAT",
                {
                    "TYPE": "FLOAT32",
                    "DIM": vector_dimension,
                    "DISTANCE_METRIC": "COSINE",
                },
                as_name="vector",
            ),
        )
        definition = IndexDefinition(prefix=["chunks:"], index_type=IndexType.JSON)
        self.client.ft("idx:chunks_vss").create_index(
            fields=schema, definition=definition
        )
