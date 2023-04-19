import json
from typing import Any

from langchain.document_loaders.notiondb import NotionDBLoader, PAGE_URL
from langchain.vectorstores.pgvector import PGVector
from langchain.schema import Document

from sapientone.vendors.pgvector import VectorRepo


class SapientoneNotionDBLoader(NotionDBLoader):
    """The LangChain DB Loader doesn't save date fields"""

    def load_page(self, page_id: str) -> Document:
        """Read a page."""
        data = self._request(PAGE_URL.format(page_id=page_id))

        # load properties as metadata
        metadata: dict[str, Any] = {}

        for prop_name, prop_data in data["properties"].items():
            prop_type = prop_data["type"]

            if prop_type == "rich_text":
                value = prop_data["rich_text"][0]["plain_text"] if prop_data["rich_text"] else None
            elif prop_type == "title":
                value = prop_data["title"][0]["plain_text"] if prop_data["title"] else None
            elif prop_type == "multi_select":
                value = [item["name"] for item in prop_data["multi_select"]] if prop_data["multi_select"] else []
            elif prop_type == "date":
                if prop_data["date"]["end"]:
                    value = prop_data["date"]["end"]
                elif prop_data["date"]["start"]:
                    value = prop_data["date"]["start"]
                else:
                    value = None

            else:
                value = None

            metadata[prop_name.lower()] = value

        metadata["id"] = page_id

        return Document(page_content=self._load_blocks(page_id), metadata=metadata)


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
        notion_loader: SapientoneNotionDBLoader,
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
