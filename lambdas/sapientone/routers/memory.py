from typing import Annotated, Type

from fastapi import APIRouter, Depends
from langchain.schema import Document
from langchain.document_loaders.notiondb import NotionDBLoader

from pydantic import BaseModel

from sapientone.auth import api_key_auth
from sapientone.dependencies import (
    ExpectedEnvironmentVariables,
    PGVectorStore,
    get_env_vars,
    get_vectorstore_class,
)
from sapientone.vendors.pgvector import VectorRepo
from sapientone.vendors.notion import NotionRepo, TextRepo

router = APIRouter(dependencies=[Depends(api_key_auth)])


class AppendToIndexRow(BaseModel):
    text: str
    metadata: dict[str, str]


class AppendToIndexPayload(BaseModel):
    index_name: str
    rows: list[AppendToIndexRow]


def _ingest_documents(document_ids: list[str], repo: VectorRepo):
    operations = []

    for document_id in document_ids:
        _document, operation = repo.load_document(document_id)
        operations.append(
            {
                "document_id": document_id,
                "operation": operation,
            }
        )

    response_body = {
        "data": {"operations": operations},
    }

    return response_body


@router.post("/append/text")
def http_index_append_text(
    payload: AppendToIndexPayload,
    env_vars: Annotated[ExpectedEnvironmentVariables, Depends(get_env_vars)],
    VectorClass: Annotated[Type[PGVectorStore], Depends(get_vectorstore_class)],
):
    db = VectorClass(env_vars.PGVECTOR_CONNECTION_STRING, payload.index_name)
    documents = [
        Document(
            page_content=row.text,
            metadata={
                "id": TextRepo.assign_document_id(row.text, row.metadata),
                **row.metadata,
            },
        )
        for row in payload.rows
    ]
    repo = TextRepo(db.vectorstore, documents)
    document_ids = [document.metadata["id"] for document in documents]

    response_body = _ingest_documents(document_ids, repo)

    return response_body


class AppendNotionPagePayload(BaseModel):
    index_name: str
    page_ids: list[str]
    notion_integration_token: str


@router.post("/append/notion")
def http_index_append_notion(
    payload: AppendNotionPagePayload,
    env_vars: Annotated[ExpectedEnvironmentVariables, Depends(get_env_vars)],
    VectorClass: Annotated[Type[PGVectorStore], Depends(get_vectorstore_class)],
):
    db = VectorClass(env_vars.PGVECTOR_CONNECTION_STRING, payload.index_name)
    loader = NotionDBLoader(integration_token=payload.notion_integration_token, database_id="unused")

    repo = NotionRepo(db.vectorstore, loader)

    response_body = _ingest_documents(payload.page_ids, repo)

    return response_body
