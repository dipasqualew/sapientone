import json

from langchain.document_loaders.notiondb import NotionDBLoader
from langchain.vectorstores.pgvector import PGVector
from langchain.schema import Document

from sapientone.vendors.pgvector import VectorRepo


class TextRepo(VectorRepo):
    def __init__(self, pgvector: PGVector, documents: list[Document]):
        super().__init__(pgvector)
        self._documents = {
            self.assign_document_id(document.page_content, document.metadata): document for document in documents
        }

    @classmethod
    def assign_document_id(self, content: str, metadata: dict[str, str]):
        metadata_id = metadata.get("id")

        if metadata_id:
            return metadata_id

        return self._hash_content(content)

    def _get_document(self, document_id: str) -> Document:
        return self._documents[document_id]


class NotionRepo(VectorRepo):
    def __init__(
        self,
        pgvector: PGVector,
        notion_loader: NotionDBLoader,
        prepend_metadata: bool = True,
    ):
        super().__init__(pgvector)
        self.notion = notion_loader
        self.prepend_metadata = prepend_metadata

    def _get_document(self, document_id: str) -> Document:
        document = self.notion.load_page(document_id)

        # add metadata
        if self.prepend_metadata:
            document.page_content = json.dumps(document.metadata) + "\n\n" + document.page_content

        return document
