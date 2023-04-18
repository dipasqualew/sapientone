from typing import Annotated, Type
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from sapientone.auth import api_key_auth
from sapientone.dependencies import (
    PGVectorStore,
    get_vectorstore_class,
    ExpectedEnvironmentVariables,
    get_env_vars,
)

router = APIRouter(dependencies=[Depends(api_key_auth)])


class AnswerQuestionPayload(BaseModel):
    question: str
    index_name: str


@router.post("/question")
def http_answer(
    payload: AnswerQuestionPayload,
    env_vars: Annotated[ExpectedEnvironmentVariables, Depends(get_env_vars)],
    VectorClass: Annotated[Type[PGVectorStore], Depends(get_vectorstore_class)],
):
    vectorstore = VectorClass(env_vars.PGVECTOR_CONNECTION_STRING, payload.index_name)
    answer = vectorstore.query(payload.question)

    response_body = {
        "data": {
            "question": payload.question,
            "answer": answer,
        }
    }

    return response_body
