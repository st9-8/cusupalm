######################################################################################################
#    This file will be used to retrieve data from various sources for the demo application           #
######################################################################################################

import os
from decouple import config

from langchain_community.tools import TavilySearchResults
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ai.enums import DataType, DataSourceType
from ai.retrievers.base import BaseRetriever

from ai.vectorizers.chroma import ChromaClient
from ai.vectorizers.base import VectorDBBaseClient

os.environ['TAVILY_API_KEY'] = config('TAVILY_API_KEY')


class TavilyRetriever(BaseRetriever):
    APP = 'TAVILY'

    def load_vectordb_client(self, host: str = None, port: int = None,
                             load_from_config: bool = True) -> VectorDBBaseClient:
        client = ChromaClient(host=host, port=port, load_from_config=load_from_config)

        return client

    def get_articles(self, subject: str = None, limit: int = None) -> list:
        research_tool = TavilySearchResults(
            max_results=5,
            search_depth="advanced"
        )
        # Returns a list of url in the form [{'url': '', 'content': ''}, ...]
        results = research_tool.invoke({'query': subject})
        splits = []

        # Now let's chunk the provided data and store them in the vector store
        for result in results:
            loader = WebBaseLoader(web_path=[result['url']])

            docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
            documents = text_splitter.split_documents(docs)
            for index, split in enumerate(documents):
                split.metadata.update(
                    {
                        'title': f'Split {index} of {result["url"]}',
                        'link': result['url']
                    }
                )

                splits.append(split)

        return splits


if __name__ == '__main__':
    # How to use the retriever
    retriever = TavilyRetriever()
    articles = retriever.get_articles(subject='Google Developers Groups')
    retriever.embed_articles(articles=articles, data_type=DataType.WEB_LINK, data_source=DataSourceType.WEB)

    # Or
    retriever = TavilyRetriever()
    retriever.embed_articles(subject='Google Developers Groups', data_type=DataType.WEB_LINK,
                             data_source=DataSourceType.WEB)
