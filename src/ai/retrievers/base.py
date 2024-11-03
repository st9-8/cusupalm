# This module contains the base retriever class, with this one, you can create your own retriever   #
# it can be a retriever for your E-commerce company mails, your Cash app company whatsapp message,  #
# your company FAQs, ...                                                                            #
# This project only provides a web retriever using Tavily                                           #
#####################################################################################################

import abc
import logging
import requests

from ai.vectorizers.base import VectorDBBaseClient

from ai.enums import DataType
from ai.enums import DataSourceType

from ai.models import AIResource


class BaseRetriever(abc.ABC):
    """
        This base class assume that there are some kind of documents(tickets, articles, faqs, tutorials)
         which can be used as knowledge base, feel free to add more
    """
    APP = None

    def __init__(self, username: str = None, password: str = None, token: str = None):
        self.logger = logging.getLogger()
        if (username and password) or token:
            self.session: requests.Session = self.authenticate(username, password, token)
        self.vector_db_client: VectorDBBaseClient = self.load_vectordb_client()

    def authenticate(self, username: str = None, password: str = None, token: str = None) -> requests.Session:
        raise NotImplemented()

    def load_vectordb_client(self, host: str = None, port: int = None,
                             load_from_config: bool = True) -> VectorDBBaseClient:
        raise NotImplemented()

    def embed_data(self, data_type: DataType, data_source: DataSourceType, data: list, limit: int = None) -> None:
        collection_name = f'{self.APP}_COLLECTION'
        collection = self.vector_db_client.get_or_create_collection(
            name=collection_name,
            metadata={
                'app': self.APP,
                'name': data_type,
                'description': f'Data collection built from {data_source} of {self.APP}'
            }
        )

        for document in data:
            document.metadata['source'] = self.APP
            document.metadata['title'] = document.metadata['title']

            ai_resource, created = AIResource.objects.get_or_create(
                app=self.APP,
                link=document.metadata['link'],
                data_type=data_type,
                content=document.page_content,
                metadata=document.metadata
            )

            if created:
                document.metadata.update(
                    {
                        'ai_resource': ai_resource.id,
                    }
                )
                self.logger.info(f'Document metadata: {document.metadata}')
                self.vector_db_client.save_documents(
                    documents=[document.page_content],
                    collection=collection,
                    ids=[str(document.metadata.get('ai_resource'))],
                    metadata=[document.metadata],
                    create_or_update=True
                )

    def get_faqs(self, limit: int = None, subject: str = None) -> list:
        return []

    def embed_faqs(self, faqs: list = None, limit: int = None) -> None:
        faqs = faqs or self.get_faqs(limit)
        self.logger.info(f'Start embedding {len(faqs)} faqs...')
        self.embed_data(DataType.TEXT, DataSourceType.APP_FAQ, faqs, limit)

    def get_articles(self, limit: int = None, subject: str = None) -> list:
        return []

    def embed_articles(self, articles: list = None, limit: int = None, data_type: DataType = DataType.TEXT,
                       data_source: DataSourceType = DataSourceType.APP_TUTORIAL, subject: str = None) -> None:
        articles = articles or self.get_articles(limit, subject=subject)
        self.logger.info(f'Start embedding of {len(articles)} articles...')
        self.embed_data(data_type, data_source, articles, limit)
        self.logger.info('Articles embedding completed')

    def get_tickets(self, limit: int = None) -> list:
        return []

    def embed_tickets(self, tickets: list = None, limit: int = None, subject: str = None, ) -> None:
        tickets = tickets or self.get_tickets(limit)
        self.logger.info(f'Start embedding of {len(tickets)} tickets...')
        self.embed_data(DataType.TEXT, DataSourceType.APP_TICKET, tickets, limit)
        self.logger.info('Tickets embedding completed')

    def get_settings(self, limit: int = None) -> list:
        return []

    def embed_settings(self, settings: list = None, limit: int = None) -> None:
        settings = settings or self.get_settings(limit)
        self.logger.info(f'Start embedding {len(settings)} settings...')
        self.embed_data(DataType.TEXT, DataSourceType.APP_GUIDE, settings, limit)
        self.logger.info('Settings embedding completed')

    def run(self, limit: int = None, with_embeddings: bool = False, subject: str = None, ) -> dict:
        if with_embeddings:
            faqs = self.get_faqs(limit, subject=subject)
            self.embed_faqs(faqs, limit)
            articles = self.get_articles(limit, subject=subject)
            self.embed_articles(articles, limit)
            tickets = self.get_tickets(limit)
            self.embed_tickets(tickets, limit)
            settings = self.get_settings(limit)
            self.embed_settings(settings, limit)
        else:
            faqs = self.get_faqs(limit, subject=subject)
            articles = self.get_articles(limit, subject=subject)
            tickets = self.get_tickets(limit)
            settings = self.get_settings(limit)

        results = {
            'data': {
                'faqs': faqs,
                'articles': articles,
                'tickets': tickets,
                'settings': settings
            }
        }

        return results
