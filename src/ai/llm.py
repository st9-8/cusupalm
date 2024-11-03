from __future__ import annotations

import os
import logging

from django.contrib.auth import get_user_model

from chromadb.config import Settings
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import AIMessage
from langchain_core.messages import HumanMessage
from sympy.physics.units import temperature

from traceback_with_variables import format_exc

from core.models import Ticket

from ai.vectorizers.chroma import ChromaClient

from decouple import config

User = get_user_model()

os.environ['LANGCHAIN_TRACING_V2'] = config('LANGCHAIN_TRACING_V2')
os.environ['LANGCHAIN_API_KEY'] = config('LANGSMITH_API_KEY')

logger = logging.getLogger('llm')

# Lower temperature will make the model more deterministic
llm = ChatOllama(model_name=config('OLLAMA_MODEL'), temperature=0.0)


def get_session_history(session_id: int) -> ChatMessageHistory:
    """
        The aim of this function is to get the history of the ticket. We consider that the ticket is the initial message,
        then each of the comment is a message in the conversation. To provide accurate answer, we have to give to the model this discussion information.
        :param session_id: The ticket id is used as session id of the LLM
        :return: The history of the ticket in Langchain format, usable by any ChatLLM
    """
    logger.info(f'Getting session history for ticket #{session_id}')
    ticket = Ticket.objects.get(id=session_id)
    history = ticket.get_history()

    logger.info(f'History extracted: {history}')

    chat_history = ChatMessageHistory()
    chat_history.add_message(HumanMessage(content=history["initial_message"]))

    for message in history["thread"]:
        role = message["role"]
        content = message["text"]
        message = AIMessage(content=content) if role == 'agent' else HumanMessage(content=content)
        chat_history.add_message(message)

    return chat_history


def generate_answer(question: str, ticket_id: int, app_name: str = None):
    """
        @question: the ticket or comment on which we need a response
        @history: the thread history of the ticket if exists
        @app_name: The of the app (retrieve most of the time) used, it's also use to build collection name in the vectorstore
    """

    # TODO: Initially wanted to use my Chroma vectorstore as retriever, but not working as wanted, we will later,
    #  so I did it manually. I think it's due to some issue with some deprecated packages: Langchain chroma
    # Technical debt 😁

    # huggingface_embedding = HuggingFaceEmbeddings(
    #     model_name='paraphrase-multilingual-MiniLM-L12-v2',
    #     model_kwargs={'device': 'cpu'},
    #     encode_kwargs={'normalize_embeddings': False}
    # )

    # Chroma client settings
    # chroma_settings = Settings()
    # chroma_settings.chroma_server_host = config('CHROMA_HOST')
    # chroma_settings.chroma_server_http_port = config('CHROMA_PORT')
    # logger.info(f"Loading vectorstore collection {f'{app_name}_COLLECTION'}")
    # vectorstore = Chroma(
    #     client_settings=chroma_settings,
    #     embedding_function=huggingface_embedding,
    #     collection_name=f'{app_name}_COLLECTION'
    # )
    # retriever = vectorstore.as_retriever(
    #     search_kwargs={
    #         'k': 5
    #     }
    # )

    # Manual usage as I told earlier
    chroma_client = ChromaClient()
    results = chroma_client.query_documents(question, f'{app_name}_COLLECTION', metadata_filter={}, n_results=3)
    logger.info(f'Results from vectorstore {results}')

    prompt = PromptTemplate.from_template(
        """
        You are an assistant for a support system. You should use the retrieved context to answer the tickets of users 
        if necessary; if not, simply answer the question. If you don't know the answer, just say so. Please provide 
        your response in a professional email format. Always keep the response as short as possible, three sentences 
        maximum. They can exceed only if it's relevant for the answer.
        Question: {question}
        Context: {context}
        Answer:
        """
    )

    def format_docs(docs):
        return '\n\n'.join([doc[0]['description'] for doc in docs['metadatas']])

    extract_input = RunnableLambda(lambda x: x['input'])
    results = RunnableLambda(
        lambda q: chroma_client.query_documents(q, f'{app_name}_COLLECTION', metadata_filter={}, n_results=3))
    runnable = (
            extract_input
            | {'context': results | format_docs, 'question': RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )

    runnable_with_history = RunnableWithMessageHistory(
        runnable,
        get_session_history,
        input_messages_key='input',
        history_messages_key='history'
    )

    response = runnable_with_history.invoke({
        'input': question
    }, config={'configurable': {'session_id': ticket_id}})

    return response


# It's a little bit time-consuming, depending on the speed of the model. You can set it as celery task for example.
def handling_response_generation(ticket_id: int | None, comment_id: int | None, is_comment: bool = None):
    """
        The aim of this task is to handle all the process of generating the response of the ticket
        - Generate a response to the ticket
        - Set as temporal response in AITemporaryComment model
        - Send mails and notification to the company managers with the proposal response

        @ticket_id: the id of the ticket object if it's a ticket object
        @comment_id: the id of the comment object if it's a comment object
        @is_comment: True if it's a comment object, False if it's a ticket object
    """
    from core.models import Ticket
    from core.models import Comment
    from ai.models import AITemporalComment

    from core.utils import send_simple_mail

    try:
        if is_comment:
            comment = Comment.objects.get(id=comment_id)
            content = comment.content

            # Generate response
            # Handle context (history of the message with chat history feature of LLM)
            response_proposal = generate_answer(content, comment.ticket.id, app_name=comment.ticket.app)

            # Save the temporal response
            AITemporalComment.objects.create(
                comment=comment,
                content=response_proposal,
                app=comment.ticket.app
            )

            notification_email = f"""
            Hello dear manager,

            We received a response to ticket #{comment.ticket} from {comment.ticket.open_by_email}.
            We created a comment for this email and our AI generated a response proposal for that, please take a look:

            {response_proposal}

            ------

            You can go to your dashboard to update and/or validate this response before sending it to the customer.
            """

            to_subject = f'Validation of AI Response on ticket #{comment.ticket.id}'
        else:
            ticket = Ticket.objects.get(id=ticket_id)

            content = f'{ticket.title}\n\n{ticket.description}'

            # Generate response
            response_proposal = generate_answer(content, ticket.id, app_name=ticket.app)

            # Save the temporal response
            AITemporalComment.objects.create(
                ticket=ticket,
                content=response_proposal,
                app=ticket.app
            )

            notification_email = f"""
            Hello dear manager,

            We received a ticket from {ticket.open_by_email}.
            We created a ticket for this email and our AI generated a response proposal for that, please take a look:

            {response_proposal}

            ------

            You can go to your dashboard to update and/or validate this response before sending it to the customer.
            """

            to_subject = f'Validation of AI Response on ticket #{ticket.id}'

        # Send mail to the company agents
        agents = User.objects.filter(is_staff=True)
        agents_email = [agent.email for agent in agents]

        send_simple_mail(to=agents_email, subject=to_subject, message=notification_email)
    except Comment.DoesNotExist:
        logger.error(f'Comment {comment_id} not found')
        return False
    except Ticket.DoesNotExist:
        logger.error(f'Ticket {ticket_id} not found')
        return False
    except Exception as e:
        logger.error(format_exc(e))
        return False
