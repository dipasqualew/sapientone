from langchain.document_loaders import NotionDBLoader
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings

from langchain.vectorstores import VectorStore, Pinecone

import pinecone


def get_notion_documents(notion_token: str, notion_database_id: str) -> list[Document]:
    loader = NotionDBLoader(notion_token, notion_database_id)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " "],
        chunk_size=200,
        chunk_overlap=0,
    )

    splits = splitter.split_documents(docs)

    return splits


def index_in_chroma(docs: list[Document]) -> VectorStore:
    embeddings = OpenAIEmbeddings()  # type: ignore[call-arg] # Typing is wrong here
    db = Chroma.from_documents(docs, embeddings)

    return db


def _init_pinecone(pinecone_api_key: str, pinecone_env: str):
    pinecone.init(
        api_key=pinecone_api_key,  # find at app.pinecone.io
        environment=pinecone_env,  # next to api key in console
    )


def _create_pinecone_index(index_name: str, pinecone_api_key: str, pinecone_env: str):
    _init_pinecone(pinecone_api_key, pinecone_env)

    pinecone.create_index(
        name=index_name,
        dimension=1536,  # dimensionality of dense model
        metric="dotproduct",  # sparse values supported only for dotproduct
        pod_type="s1",
        metadata_config={"indexed": []},  # see explaination above
    )


def _delete_pinecone_index(index_name: str, pinecone_api_key: str, pinecone_env: str):
    _init_pinecone(pinecone_api_key, pinecone_env)

    pinecone.delete_index(index_name)


def _clear_pinecone_index(index_name: str) -> None:
    pinecone.Index(index_name).delete(deleteAll="true")


def index_in_pinecone(
    docs: list[Document],
    index_name: str,
    pinecone_api_key: str,
    pinecone_env: str,
    create_index: bool = False,
    clear_index: bool = True,
) -> VectorStore:
    _init_pinecone(pinecone_api_key, pinecone_env)
    embeddings = OpenAIEmbeddings()  # type: ignore[call-arg] # Typing is wrong here

    if create_index:
        _create_pinecone_index(index_name, pinecone_api_key, pinecone_env)

    if clear_index:
        pinecone.Index(index_name).delete(deleteAll="true")

    db = Pinecone.from_documents(docs, embeddings, index_name=index_name)

    return db


def get_pinecone_retriever(
    index_name: str,
    pinecone_api_key: str,
    pinecone_env: str,
) -> VectorStore:
    _init_pinecone(pinecone_api_key, pinecone_env)
    embeddings = OpenAIEmbeddings()  # type: ignore[call-arg] # Typing is wrong here

    db = Pinecone.from_existing_index(index_name, embedding=embeddings)

    return db
