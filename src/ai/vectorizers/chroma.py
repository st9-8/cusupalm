from __future__ import annotations

import chromadb
from chromadb.utils import embedding_functions

from traceback_with_variables import format_exc

from decouple import config

from .base import VectorDBBaseClient


class ChromaClient(VectorDBBaseClient):
    DEFAULT_EMBEDDING = None
    NAME = 'CHROMA'

    def __init__(self, host: str = None, port: int = None, load_from_config: bool = True):
        super(ChromaClient, self).__init__(host, port, load_from_config)

        self.DEFAULT_EMBEDDING = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name='paraphrase-multilingual-MiniLM-L12-v2')
        try:
            self.client = chromadb.HttpClient(self.host, self.port, headers={
                'X-Chroma-Token': config('CHROMA_TOKEN')})
            self.logger.info(f'Chroma client initialized, running at {config("CHROMA_HOST")}:{config("CHROMA_PORT")}')
        except Exception:
            raise ValueError(f'Unable to initialize Chroma client at {config("CHROMA_HOST")}:{config("CHROMA_PORT")}')

    def get_collection(self, name: str) -> chromadb.Collection:
        return self.client.get_or_create_collection(name)

    def save_documents(self, documents: list[str], collection: str | chromadb.Collection, ids: list[str],
                       metadata: list[dict], create_or_update=False) -> None:
        collection = self.get_or_create_collection(collection) if isinstance(collection, str) else collection

        self.logger.info(f'Saving {len(documents)} documents to {collection.name}')
        if create_or_update:
            collection.upsert(
                documents=documents,
                metadatas=metadata,
                ids=ids
            )
        else:
            collection.add(
                documents=documents,
                metadatas=metadata,
                ids=ids
            )

    def query_documents(self, query: str | list[str], collection: str | chromadb.Collection, metadata_filter: dict,
                        n_results: int = 5) -> dict:
        collection = self.get_collection(collection) if isinstance(collection, str) else collection
        result = collection.query(
            query_texts=[query] if isinstance(query, str) else query,
            where=metadata_filter,
            n_results=n_results
        )

        return result

    def get_or_create_collection(self, name: str, metadata: dict = None,
                                 embedding_function: callable = None) -> chromadb.Collection:
        embedding_function = embedding_function or self.DEFAULT_EMBEDDING

        if not metadata:
            collection = self.client.get_or_create_collection(
                name=name,
                embedding_function=embedding_function
            )
        else:
            collection = self.client.get_or_create_collection(
                name=name,
                metadata=metadata,
                embedding_function=embedding_function
            )

        return collection

    def client_healthcheck(self) -> bool:
        try:
            self.client.heartbeat()
            return True
        except Exception as e:
            self.logger.error(format_exc(e))
            return False

    def count(self, collection: str | chromadb.Collection) -> int:
        collection = self.get_collection(collection)

        return collection.count()

    def reset_db(self) -> None:
        self.client.reset()
