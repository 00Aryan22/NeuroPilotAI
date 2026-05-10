import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
# LangChain changed splitter imports across versions; keep both paths compatible.
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from utils.config import get_secret

load_dotenv()


class VectorStoreManager:
    """Lightweight wrapper for persistent Chroma PDF collections."""

    def __init__(self, persist_root: str = "vector_db") -> None:
        self.persist_root = Path(persist_root)
        self.persist_root.mkdir(parents=True, exist_ok=True)
        self.embedding = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=get_secret("OPENROUTER_API_KEY"),
            base_url=get_secret("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        )

    @staticmethod
    def chunk_text(text: str) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", " ", ""],
        )
        return splitter.split_text(text)

    def build_pdf_store(self, session_id: str, text: str) -> Chroma:
        chunks = self.chunk_text(text)
        ids = [f"{session_id}-{idx}" for idx in range(len(chunks))]
        db_path = self.persist_root / f"pdf_{session_id}"
        vector_store = Chroma.from_texts(
            texts=chunks,
            embedding=self.embedding,
            ids=ids,
            persist_directory=str(db_path),
            collection_name=f"pdf_collection_{session_id}",
        )
        # Newer langchain-chroma persists automatically; older versions expose .persist().
        if hasattr(vector_store, "persist"):
            vector_store.persist()
        return vector_store

    def load_pdf_store(self, session_id: str) -> Chroma:
        db_path = self.persist_root / f"pdf_{session_id}"
        return Chroma(
            embedding_function=self.embedding,
            persist_directory=str(db_path),
            collection_name=f"pdf_collection_{session_id}",
        )
