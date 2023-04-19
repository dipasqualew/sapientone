from typing import Union

import httpx
from pytest_bdd import given, then, parsers, when
from langchain.vectorstores.pgvector import PGVector, EmbeddingStore
from langchain.schema import Document
from sqlalchemy.orm import Session


from sapientone.dependencies import ExpectedEnvironmentVariables
from sapientone.vendors.pgvector import get_pgvector

from ..conftest import SapientoneTestClient

QA = {
    "What is my favourite pizza?": "Viennese",
    "What did I study?": "Philosophy",
}


def _clean_collection(pgvector: PGVector):
    with Session(pgvector._conn) as session:
        collection = pgvector.get_collection(session)

        if not collection:
            raise ValueError("Collection not found")

        _query = (
            session.query(EmbeddingStore)
            .filter(EmbeddingStore.collection_id == collection.uuid)
            .delete(synchronize_session=False)
        )

        session.commit()


@given(
    parsers.parse('an index named "{index_name}"'),
    target_fixture="bdd_index_name",
)
def an_index_named_index_name(test_type: str, index_name: str, env_vars: ExpectedEnvironmentVariables):
    if test_type == "integration":
        pgvector = get_pgvector(env_vars.PGVECTOR_CONNECTION_STRING, index_name)

        pgvector.create_collection()
        _clean_collection(pgvector)

        yield index_name

        _clean_collection(pgvector)

    else:
        yield index_name


@given(
    parsers.parse('an index named "{index_name}" doesn\'t exist'),
    target_fixture="bdd_index_name",
)
def an_index_named_index_name_doesnt_exist(test_type: str, index_name: str, env_vars: ExpectedEnvironmentVariables):
    if test_type == "integration":
        pgvector = get_pgvector(env_vars.PGVECTOR_CONNECTION_STRING, index_name)
        pgvector.delete_collection()

        yield index_name

        _clean_collection(pgvector)

    else:
        yield index_name


@given(parsers.parse('the index contains the text "{text}"'))
def the_index_contains_the_text(test_type: str, bdd_index_name: str, env_vars: ExpectedEnvironmentVariables, text: str):
    if test_type == "integration":
        document = Document(page_content=text, metadata={})
        pgvector = get_pgvector(env_vars.PGVECTOR_CONNECTION_STRING, bdd_index_name)
        pgvector.add_documents([document])


@then(parsers.parse('the request returns http code "{http_code}"'))
def the_request_returns_http_code_http_code(bdd_http_response: httpx.Response, http_code: str):
    assert bdd_http_response.status_code == int(http_code)


@when(
    parsers.parse('the user asks "{question}" with the "{api_key_name}" API Key'),
    target_fixture="bdd_http_response",
)
def the_user_asks_question(
    api_key_name: str,
    env_vars: ExpectedEnvironmentVariables,
    bdd_index_name: str,
    client: Union[SapientoneTestClient, httpx.Client],
    question: str,
):
    if isinstance(client, SapientoneTestClient):
        client.set_query_result(QA[question])

    if api_key_name == "correct":
        api_key = env_vars.SAPIENTONE_API_KEY
        client.headers["Authorization"] = f"Bearer {api_key}"

    elif api_key_name == "incorrect":
        api_key = "incorrect-api-key"
        client.headers["Authorization"] = f"Bearer {api_key}"

    client.headers["Content-Type"] = "application/json"

    response = client.post(
        "/query/question",
        json={
            "question": question,
            "index_name": bdd_index_name,
        },
    )

    return response


@then(parsers.parse('the question "{question}" is answered with "{answer}"'))
def the_question_question_is_answered_with_answer(
    bdd_http_response: httpx.Response,
    question: str,
    answer: str,
):
    json_data = bdd_http_response.json()

    assert json_data["data"]["question"] == question
    assert json_data["data"]["answer"] == answer


@then(parsers.parse('the question "{question}" contains "{answer}"'))
def the_question_question_contains_answer(
    bdd_http_response: httpx.Response,
    question: str,
    answer: str,
):
    json_data = bdd_http_response.json()

    assert json_data["data"]["question"] == question
    assert answer in json_data["data"]["answer"]
