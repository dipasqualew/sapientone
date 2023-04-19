import os

import click
import httpx

from langchain.document_loaders.notiondb import NotionDBLoader


@click.group("notion")
def notion_cli():
    pass


@click.group("memory-service")
def memory_service():
    pass


@memory_service.command()
@click.option("--sapientone-token", required=True, default=lambda: os.environ.get("SAPIENTONE_API_KEY"))
@click.option("--sapientone-api-url", required=True, default=lambda: os.environ.get("SAPIENTONE_API_URL"))
@click.option("--index-name", required=True)
@click.option("--question", required=True)
def question(sapientone_token: str, sapientone_api_url: str, index_name: str, question: str):
    print(f"Asking '{question}' in index: '{index_name}'...\n")
    headers = {
        "Authorization": f"Bearer {sapientone_token}",
        "Content-Type": "application/json",
    }
    full_url = f"{sapientone_api_url}/query/question"

    payload = {
        "index_name": index_name,
        "question": question,
    }

    response = httpx.post(full_url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    answer = response.json()["data"]["answer"]

    print(f"--> Answer: '{answer}'")


def _notion__index_page(
    sapientone_token: str,
    notion_token: str,
    index_name: str,
    url: str,
    page_ids: list[str],
) -> None:
    print(f"Starting to index notion pages for index: '{index_name}'...\n")
    headers = {
        "Authorization": f"Bearer {sapientone_token}",
        "Content-Type": "application/json",
    }
    full_url = f"{url}/memory/append/notion"

    for page_id in page_ids:
        payload = {
            "index_name": index_name,
            "page_ids": [page_id],
            "notion_integration_token": notion_token,
        }

        print(f"\n> Now indexing '{page_id}'...")

        response = httpx.post(full_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        print(f"--> Response: '{response.json()}'")

    print("\nDone!")


def _notion__index_database(
    sapientone_token: str,
    notion_token: str,
    index_name: str,
    url: str,
    database_id: str,
) -> None:
    print(f"Fetching database '{database_id}' pages...")

    loader = NotionDBLoader(notion_token, database_id)
    page_ids = loader._retrieve_page_ids()

    _notion__index_page(sapientone_token, notion_token, index_name, url, page_ids)


@notion_cli.command()
@click.option("--sapientone-api-token", required=True, default=lambda: os.environ.get("SAPIENTONE_API_KEY"))
@click.option("--sapientone-api-url", required=True, default=lambda: os.environ.get("SAPIENTONE_API_URL"))
@click.option("--notion-integration-key", required=True, default=lambda: os.environ.get("NOTION_INTEGRATION_KEY"))
@click.option("--index-name", required=True)
@click.option("--page-ids", required=True, multiple=True)
def notion__index_page(
    sapientone_api_token: str,
    sapientone_api_url: str,
    notion_integration_key: str,
    index_name: str,
    page_ids: list[str],
) -> None:
    _notion__index_page(
        sapientone_api_token,
        notion_integration_key,
        index_name,
        sapientone_api_url,
        page_ids,
    )


@notion_cli.command()
@click.option("--sapientone-api-token", required=True, default=lambda: os.environ.get("SAPIENTONE_API_KEY"))
@click.option("--sapientone-api-url", required=True, default=lambda: os.environ.get("SAPIENTONE_API_URL"))
@click.option("--notion-integration-key", required=True, default=lambda: os.environ.get("NOTION_INTEGRATION_KEY"))
@click.option("--index-name", required=True)
@click.option("--database-id", required=True)
def notion__index_database(
    sapientone_api_token: str,
    sapientone_api_url: str,
    notion_integration_key: str,
    index_name: str,
    database_id: str,
) -> None:
    _notion__index_database(sapientone_api_token, notion_integration_key, index_name, sapientone_api_url, database_id)


if __name__ == "__main__":
    main = click.CommandCollection(sources=[memory_service, notion_cli])
    main()
