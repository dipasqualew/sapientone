import os
from typing import Iterable, Union
from unittest.mock import MagicMock

import pytest
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from langchain.schema import Document

from sapientone.app import app
from sapientone.dependencies import (
    ExpectedEnvironmentVariables,
    PGVectorStore,
    get_vectorstore_class,
    get_env_vars,
)

load_dotenv()


class MockPGVectorStore(PGVectorStore):
    def __init__(self, *args, **kwargs):
        self._query_result = ""
        self.vectorstore = MagicMock()

    def add_documents(self, documents: list[Document]) -> None:
        pass

    def query(self, query: str) -> str:
        return self._query_result


class SapientoneTestClient(TestClient):
    def __init__(self, app: FastAPI, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        self.vectorstore = MockPGVectorStore("", "")

    def set_query_result(self, result: str) -> None:
        self.vectorstore._query_result = result

    def get_vectorstore_override(self):
        return lambda _x, _y: self.vectorstore


def pytest_addoption(parser):
    parser.addoption(
        "--type",
        type=str,
        action="store",
        default="unit",
        help="Test run type - unit, integration",
    )


@pytest.fixture
def test_type(request) -> str:
    return request.config.getoption("--type")


@pytest.fixture
def env_vars(test_type: str) -> ExpectedEnvironmentVariables:
    if test_type == "unit":
        return ExpectedEnvironmentVariables(
            PGVECTOR_CONNECTION_STRING="PGVECTOR_CONNECTION_STRING",
            SAPIENTONE_API_KEY="SAPIENTONE_API_KEY",
            OPENAI_API_KEY="OPENAI_API_KEY",
        )

    return ExpectedEnvironmentVariables.parse_obj(os.environ)


@pytest.fixture
def client(
    test_type: str,
    env_vars: ExpectedEnvironmentVariables,
) -> Iterable[Union[SapientoneTestClient, httpx.Client]]:
    if test_type == "unit":
        test_client = SapientoneTestClient(app)
        app.dependency_overrides[get_vectorstore_class] = lambda: test_client.get_vectorstore_override()
        app.dependency_overrides[get_env_vars] = lambda: env_vars

        yield test_client

        app.dependency_overrides = {}
    else:
        with httpx.Client(base_url="http://localhost:8080", timeout=15) as httpx_client:
            yield httpx_client
