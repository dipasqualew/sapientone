from typing import Union

import httpx
from pytest_bdd import scenario, when, parsers

from ..conftest import SapientoneTestClient
from sapientone.dependencies import ExpectedEnvironmentVariables

FEATURE = __file__.split("/")[-1][5:-3] + ".feature"


@scenario(FEATURE, "Fail to query without the correct API Key")
def test_fail_to_query_without_the_correct_api_key():
    pass


@scenario(FEATURE, "Add text and metadata to an existing index")
def test_add_text_and_metadata_to_an_existing_index():
    pass


# @scenario(FEATURE, "Add text and metadata to a new index")
# def test_add_text_and_metadata_to_a_new_index():
#     pass


@when(
    parsers.parse('the user queries with the "{api_key_name}" API Key to add "{content}"'),
    target_fixture="bdd_http_response",
)
def the_user_queries_with_the_api_key_name_to_add_content(
    api_key_name: str,
    env_vars: ExpectedEnvironmentVariables,
    bdd_index_name: str,
    client: Union[SapientoneTestClient, httpx.Client],
    content: str,
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
    json_data = {
        "rows": [
            {
                "text": content,
                "metadata": {},
            },
        ],
        "index_name": bdd_index_name,
    }
    response = client.post(
        "/memory/append/text",
        json=json_data,
    )

    return response
