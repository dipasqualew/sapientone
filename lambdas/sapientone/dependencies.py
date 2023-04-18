import os
from typing import Protocol, Type

from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from pydantic import BaseModel

from sapientone.vendors.pgvector import get_pgvector


class ExpectedEnvironmentVariables(BaseModel):
    PGVECTOR_CONNECTION_STRING: str
    OPENAI_API_KEY: str
    SAPIENTONE_API_KEY: str


class BaseVectorStore(Protocol):
    def __init__(self, index_name: str) -> None:
        ...

    def add_documents(self, documents: list[Document]) -> None:
        ...

    def query(self, query: str) -> str:
        ...


class PGVectorStore(BaseVectorStore):
    def __init__(self, connection_string: str, index_name: str):
        self.index_name = index_name
        self.vectorstore = get_pgvector(connection_string, index_name)

        self.prompt = PromptTemplate(
            input_variables=["query"],
            template="Only answer with the relevant content, without dot. Query: {query}",
        )

        self.llm = OpenAI(temperature=0)  # type: ignore[call-arg] # Typing is wrong here
        self.retriever = self.vectorstore.as_retriever()

        self.qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=self.retriever)

    def add_documents(self, documents: list[Document]) -> None:
        self.vectorstore.add_documents(documents)

    def query(self, query: str) -> str:
        return self.qa.run(self.prompt.format(query=query)).strip()


def get_env_vars() -> ExpectedEnvironmentVariables:
    return ExpectedEnvironmentVariables.parse_obj(os.environ)


def get_vectorstore_class() -> Type[PGVectorStore]:
    return PGVectorStore
