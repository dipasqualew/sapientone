import hashlib
from datetime import datetime
from functools import lru_cache
from typing import Literal


from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores.pgvector import EmbeddingStore, PGVector
from sqlalchemy.orm import Session


def get_connection_string(
    driver: str,
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
):
    return PGVector.connection_string_from_db_params(
        driver=driver,
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
    )


def pgvector_create_collection(collection_name: str, connection_string: str) -> PGVector:
    embeddings = OpenAIEmbeddings()

    db = PGVector.from_documents(
        embedding=embeddings,
        documents=[],
        collection_name=collection_name,
        connection_string=connection_string,
    )

    return db


@lru_cache(maxsize=20)
def get_pgvector(secret_token: str, index_name: str) -> PGVector:
    embeddings = OpenAIEmbeddings()

    return PGVector(
        embedding_function=embeddings,
        connection_string=secret_token,
        collection_name=index_name,
    )


def pgvector_update_collection(documents: list[Document], collection_name: str, connection_string: str) -> PGVector:
    db = get_pgvector(connection_string, collection_name)

    db.add_documents(documents)

    return db


VECTOR_OPERATIONS = Literal["created", "updated", "skipped"]


class VectorRepo:
    def __init__(self, vectorstore: PGVector):
        self.vectorstore = vectorstore

    @classmethod
    def _hash_content(self, content: str):
        return hashlib.sha1(content.encode("utf-8")).hexdigest()

    def load_document(self, document_id: str) -> tuple[Document, VECTOR_OPERATIONS]:
        document = self._get_document(document_id)

        if not document.page_content:
            return document, "skipped"

        operation = "created"

        content_hash = self._hash_content(document.page_content)
        existing = self._retrieve_existing_vector(document_id)

        if existing is not None:
            if existing.cmetadata["content_hash"] == content_hash:
                # Content hash has not changed, skip update
                return document, "skipped"
            else:
                # Content hash has changed, delete existing row
                self._delete_existing_vector(document_id)
                operation = "updated"

        document.metadata["last_loaded"] = str(datetime.now())
        document.metadata["content_hash"] = content_hash

        self.vectorstore.add_documents([document])

        return document, operation

    def _get_document(self, document_id: str) -> Document:
        raise NotImplementedError

    def _delete_existing_vector(self, page_id: str):
        with Session(self.vectorstore._conn) as session:
            collection = self.vectorstore.get_collection(session)

            if not collection:
                raise ValueError("Collection not found")

            query = (
                session.query(EmbeddingStore)
                .filter(EmbeddingStore.collection_id == collection.uuid)
                .filter(EmbeddingStore.cmetadata["id"].astext == page_id)
                .delete(synchronize_session=False)
            )

            session.commit()

            return query

    def _retrieve_existing_vector(self, page_id: str):
        with Session(self.vectorstore._conn) as session:
            collection = self.vectorstore.get_collection(session)

            if not collection:
                raise ValueError("Collection not found")

            query = (
                session.query(EmbeddingStore)
                .filter(EmbeddingStore.collection_id == collection.uuid)
                .filter(EmbeddingStore.cmetadata["id"].astext == page_id)
                .limit(1)
            )

            results = query.all()

            if len(results) > 0:
                return results[0]

            return None
