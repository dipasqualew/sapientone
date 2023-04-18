# Scenario: Add text and metadata to an existing index
#     Given an index named "sapientone-test"
#     When the user queries with the "correct" API Key to ingest the "Identity" Notion Page
#     Then the request returns http code "200"
#     When the user asks "What did you study?" with the "correct" API Key
#     Then the question "What did you study?" is answered with "Philosophy"
import os
from typing import Union

import httpx
import pytest
from pytest_bdd import scenario, when, parsers

from ..conftest import SapientoneTestClient
from sapientone.dependencies import ExpectedEnvironmentVariables

FEATURE = __file__.split("/")[-1][5:-3] + ".feature"


@pytest.fixture
def notion_integration_token() -> str:
    return os.environ["NOTION_INTEGRATION_KEY"]


@scenario(FEATURE, "Fail to query without the correct API Key")
def test_fail_to_query_without_the_correct_api_key():
    pass


@scenario(FEATURE, "Add text and metadata to an existing index")
def test_add_text_and_metadata_to_an_existing_index():
    pass


pages = {
    "identity": "f2b7e727c9e34c429936e71dbc5bc1e0",
}


@when(
    parsers.parse('the user queries with the "{api_key_name}" API Key to ingest the "{page_name}" Notion Page'),
    target_fixture="bdd_http_response",
)
def the_user_queries_with_the_api_key_name_to_add_content(
    api_key_name: str,
    env_vars: ExpectedEnvironmentVariables,
    bdd_index_name: str,
    notion_integration_token: str,
    client: Union[SapientoneTestClient, httpx.Client],
    page_name: str,
):
    if isinstance(client, SapientoneTestClient):
        pass

    if api_key_name == "correct":
        api_key = env_vars.SAPIENTONE_API_KEY
        client.headers["Authorization"] = f"Bearer {api_key}"

    elif api_key_name == "incorrect":
        api_key = "incorrect-api-key"
        client.headers["Authorization"] = f"Bearer {api_key}"

    client.headers["Content-Type"] = "application/json"

    page_id = pages[page_name]

    json_data = {
        "page_id": page_id,
        "notion_integration_token": notion_integration_token,
        "index_name": bdd_index_name,
    }

    response = client.post(
        "/memory/append/notion",
        json=json_data,
    )

    return response
