# This module contains the base vectorizer class, with this one, you can create your own vectorizer  #
# This project only provides a vectorizer for Chroma                                                 #
######################################################################################################

from __future__ import annotations

import abc
import logging
from typing import List

from decouple import config


class VectorDBBaseClient(abc.ABC):
    DEFAULT_EMBEDDING = None
    NAME = ''

    def __init__(self, host: str = None, port: int = None, load_from_config: bool = True):
        self.logger = logging.getLogger('vectorizer')
        if not host and not port and not load_from_config:
            self.logger.warning("You can't set `load_from_config=False` and not set host and port")
            raise ValueError("You can't set `load_from_config=False` and not set host and port")

        if load_from_config:
            self.host = config(f'{self.NAME}_HOST')
            self.port = config(f'{self.NAME}_PORT', cast=int)
        else:
            self.host = host
            self.port = port

    def save_documents(self, documents: list[str], collection: str | object, ids: list[str], metadata: list[dict],
                       create_or_update: bool = False) -> bool:
        raise NotImplemented()

    def query_documents(self, query: str | List[str], collection: str, metadata_filter: dict,
                        n_result: int = 5) -> dict:
        pass

    def get_or_create_collection(self, name: str, metadata: dict, embedding_function: callable) -> object:
        pass

    def get_collection(self, name: str) -> object:
        pass

    def get_client(self) -> object:
        pass

    def client_healthcheck(self) -> bool:
        pass

    def update_collection(self, name, data: dict) -> object:
        pass

    def count(self, collection: str) -> int:
        pass

    def reset_db(self) -> None:
        pass
