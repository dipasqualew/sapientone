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
from sapientone.vendors.notion import NotionRepo, TextRepo

router = APIRouter(dependencies=[Depends(api_key_auth)])


class AppendToIndexRow(BaseModel):
    text: str
    metadata: dict[str, str]


class AppendToIndexPayload(BaseModel):
    index_name: str
    rows: list[AppendToIndexRow]


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

    for document in documents:
        repo.load_document(document.metadata["id"])

    response_body = {
        "data": {
            "added_rows": len(documents),
            "operation": "created",
        }
    }

    return response_body


class AppendNotionPagePayload(BaseModel):
    index_name: str
    page_id: str
    notion_integration_token: str


@router.post("/append/notion")
def http_index_append_notion(
    payload: AppendNotionPagePayload,
    env_vars: Annotated[ExpectedEnvironmentVariables, Depends(get_env_vars)],
    VectorClass: Annotated[Type[PGVectorStore], Depends(get_vectorstore_class)],
):
    loader = NotionDBLoader(integration_token=payload.notion_integration_token, database_id="unused")
    db = VectorClass(env_vars.PGVECTOR_CONNECTION_STRING, payload.index_name)

    repo = NotionRepo(db.vectorstore, loader)

    _, operation = repo.load_document(payload.page_id)

    response_body = {
        "data": {
            "added_rows": 1,
            "operation": operation,
        }
    }

    return response_body
