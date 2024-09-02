# La clase Retriever está diseñada para generar contexto basado en una consulta, recuperando y procesando documentos relevantes desde la 
# caché o desde internet mediante el uso de embeddings, búsqueda, raspado y cálculos de similitud coseno.
import asyncio
import json
import time
from typing import Any, AsyncGenerator
import numpy as np
import pandas as pd
from util import logger
from models.document import Document
from retrieval.search import Searcher
from retrieval.cache import VectorDbCache
from retrieval.splitter import Splitter
from retrieval.scraper import Scraper
from retrieval.embeddings import Embeddings
from sklearn.metrics.pairwise import cosine_similarity
from models.search import SearchDoc, SearchResult


class Retriever:
    def __init__(
        self,
        cache: VectorDbCache,
        searcher: Searcher,
        scraper: Scraper,
        embeddings: Embeddings,
        splitter: Splitter,
    ) -> None:
        self.cache = cache
        self.searcher = searcher
        self.scraper = scraper
        self.embeddings = embeddings
        self.splitter = splitter

    async def get_context(
        self, query: str, cache_treshold: float = 0.85, k: int = 10
    ) -> AsyncGenerator[dict, None]:
        """Generates context based on query. It can retrieve from cache or from internet."""

        query_vector = await self.embeddings.run([query])
        documents = await self.cache.find_similar(query_vector[0], k)
        quality_cache = await self.evaluate_retrieval(documents, cache_treshold)

        logger.info(f"QUALITY CACHE: {quality_cache}")

        if quality_cache:
            search_results = SearchResult(
                items=[SearchDoc(link=doc.url) for doc in documents]
            )
        else:
            search_results = await self.searcher.run(query)

        yield {"event": "search", "data": json.dumps(search_results.model_dump())}

        if not quality_cache:
            documents = await self.search_for_documents(search_results, query_vector, k)
            await self.cache.write(documents)

        context = "\n".join([doc.text for doc in documents])
        yield {"event": "context", "data": context}

    async def search_for_documents(
        self, search_results, query_vector, k
    ) -> list[Document]:
        """Searches for relevant information on the internet."""

        start = time.perf_counter()

        results = search_results.model_dump()
        tasks = [self.scraper.fetch(item["link"]) for item in results["items"]]
        pages = await asyncio.gather(*tasks)

        end = time.perf_counter()
        logger.info(f"SCRAPE TIME: {end - start}")

        documents = []
        page_count = 0
        for page in pages:
            if page["text"]:
                page_count += 1
                splits = await self.splitter.split(page["text"])
                for split in splits:
                    documents.append({"text": split, "url": page["url"]})

        logger.info(f"SCRAPED PAGES: {page_count}")
        logger.info(f"SPLIT COUNT: {len(documents)}")

        embedding_start_time = time.perf_counter()
        texts = [doc["text"] for doc in documents]
        embeddings = await self.embeddings.run(texts)

        for i, vector in enumerate(embeddings):
            documents[i]["vector"] = vector

        embedding_time = time.perf_counter() - embedding_start_time
        logger.info(f"EMBEDDING TIME: {embedding_time}")

        relevant_documents = await self.get_most_similar(query_vector, documents, k)
        mean_score = await self.get_mean_similarity(relevant_documents)

        logger.info(f"RETRIEVAL SCORE: {mean_score}")
        return relevant_documents

    async def get_most_similar(self, query_vector, data, k=5) -> list[Document]:
        """
        Esta función recupera los textos más relevantes basándose en la similitud coseno con un vector de consulta dado.
        query_vector: El parámetro query_vector es un vector que representa la consulta para la cual deseas encontrar los textos más similares 
        basados en la similitud coseno. Se espera que sea una lista de valores numéricos que representan las características del vector de consulta.
        data: El parámetro data en el método get_most_similar se espera que sea una lista de diccionarios donde cada diccionario representa un 
        documento con claves como "text", "url" y "vector". La clave "vector" debe contener una lista que representa la representación vectorial del 
        texto del documento.
        k: El parámetro k en la función get_most_similar representa el número de textos más relevantes que deseas recuperar basándote en la similitud 
        coseno. Especifica los k documentos más similares al vector de consulta. En el fragmento de código proporcionado, k=5 es el valor 
        predeterminado (opcional).
        return: La función get_most_similar devuelve una lista de objetos Document que representan los textos más relevantes basados en la similitud 
        coseno con el vector de consulta proporcionado.
        """
        """Get most relevant texts based on cosine similarity"""

        query_vector = np.array(query_vector).reshape(1, -1)

        def compute_cosine_similarity(row):
            return cosine_similarity(query_vector, row)[0][0]

        df: Any = pd.DataFrame(data)
        df["vector"] = df["vector"].apply(lambda x: np.array(x).reshape(1, -1))
        df["similarity"] = df["vector"].apply(compute_cosine_similarity)
        similar = df.nlargest(k, "similarity")[["text", "url", "vector", "similarity"]]
        similar["vector"] = similar["vector"].apply(lambda x: x[0].tolist())

        json_docs = similar.to_dict("records")

        return [Document(**json_doc) for json_doc in json_docs]
    async def evaluate_retrieval(
       
        self, documents: list[Document], treshold: float
    ) -> bool:

        """Checks if the similarity average is high enough to use document set.
        """

      # Este bloque de código es un método llamado evaluate_retrieval dentro de la clase Retriever. 
      # Toma una lista de objetos Document como entrada y un valor de umbral. Esto es lo que hace:
        if documents:
            cache_score = sum(
                doc.similarity for doc in documents if doc.similarity is not None
            ) / len(documents)

            logger.info(f"CACHE SCORE: {cache_score}")
            return cache_score > treshold
        return False

    async def get_mean_similarity(self, documents: list[Document]) -> float:
        """
    Esta función en Python calcula el puntaje medio de similitud a partir de una lista de documentos.
    documents: El parámetro documents es una lista de objetos Document. La función calcula el puntaje medio de similitud de estos documentos 
    sumando los puntajes de similitud de cada documento (si el puntaje de similitud no es None) y luego dividiendo por el número total de 
    documentos en la lista. Si la lista está vacía, devuelve 0.
    type documents: list[Document]
    return: La función get_mean_similarity devuelve el puntaje medio de similitud calculado a partir de la lista de documentos proporcionada como
    entrada. Si la lista no está vacía, calcula el puntaje medio de similitud sumando los puntajes de similitud de todos los documentos que no 
    son None y dividiendo por el número total de documentos. Si la lista está vacía, devuelve 0.
        """
        if documents:
            score = sum(
                doc.similarity for doc in documents if doc.similarity is not None
            ) / len(documents)
            return score
        return 0
