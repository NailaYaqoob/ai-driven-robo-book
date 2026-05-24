"""Qdrant vector store service for RAG content retrieval."""

import os
from typing import List, Dict, Any, Optional
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse


# Qdrant configuration from environment
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "humanoid_robotics_textbook")

# Vector configuration (OpenAI text-embedding-3-small)
VECTOR_SIZE = 1536
DISTANCE_METRIC = models.Distance.COSINE


class VectorStoreService:
    """Service for managing Qdrant vector database operations."""

    def __init__(self):
        """Initialize Qdrant client lazily so import never fails on missing config."""
        self._client: Optional[QdrantClient] = None
        self.collection_name = QDRANT_COLLECTION_NAME

    @property
    def client(self) -> QdrantClient:
        if self._client is None:
            if not QDRANT_URL:
                raise RuntimeError(
                    "QDRANT_URL is not set. Configure it in the deployment environment."
                )
            self._client = QdrantClient(
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY,
                timeout=30,
            )
        return self._client

    async def create_collection_if_not_exists(self) -> bool:
        """
        Create the Qdrant collection if it doesn't already exist.

        Collection schema matches data-model.md:150-169:
        - Vector size: 1536 (OpenAI text-embedding-3-small)
        - Distance: Cosine similarity
        - Payload: chapter_id, module_name, week_number, language, section_title, page_url, content

        Returns:
            bool: True if collection was created, False if it already existed
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if exists:
                print(f"Collection '{self.collection_name}' already exists")
                return False

            # Create collection with configuration from data-model.md
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=DISTANCE_METRIC,
                ),
            )

            # Create payload indexes for fast filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="chapter_id",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="module_name",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="week_number",
                field_schema=models.PayloadSchemaType.INTEGER,
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="language",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )

            print(f"Collection '{self.collection_name}' created successfully")
            return True

        except UnexpectedResponse as e:
            print(f"Error creating collection: {e}")
            raise

    async def upsert_chunks(
        self,
        chunks: List[Dict[str, Any]],
    ) -> int:
        """
        Insert or update content chunks in the vector store.

        Args:
            chunks: List of dictionaries with keys:
                - id: str (UUID)
                - vector: List[float] (1536-dim embedding)
                - payload: Dict with chapter_id, module_name, week_number, language, section_title, page_url, content

        Returns:
            int: Number of chunks successfully upserted
        """
        if not chunks:
            return 0

        points = [
            models.PointStruct(
                id=chunk["id"],
                vector=chunk["vector"],
                payload=chunk["payload"],
            )
            for chunk in chunks
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        return len(chunks)

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        chapter_filter: Optional[str] = None,
        language: str = "en",
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content chunks using semantic similarity.

        Args:
            query_vector: Query embedding vector (1536-dim)
            top_k: Number of results to return (default: 5)
            chapter_filter: Optional chapter ID to filter results
            language: Language to filter by (default: "en")

        Returns:
            List of dicts with:
                - id: str (chunk ID)
                - score: float (similarity score)
                - payload: Dict (metadata + content)
        """
        # Build query filter
        must_conditions = [
            models.FieldCondition(
                key="language",
                match=models.MatchValue(value=language),
            )
        ]

        if chapter_filter:
            must_conditions.append(
                models.FieldCondition(
                    key="chapter_id",
                    match=models.MatchValue(value=chapter_filter),
                )
            )

        query_filter = models.Filter(must=must_conditions)

        # Execute search
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter,
        )

        # Format results
        return [
            {
                "id": str(hit.id),
                "score": hit.score,
                "payload": hit.payload,
            }
            for hit in search_result
        ]

    async def delete_by_page_path(self, page_path: str) -> int:
        """
        Delete all chunks for a specific page (used when content is updated).

        Args:
            page_path: Path to the page (e.g., "docs/02-ros2-fundamentals/week-03.mdx")

        Returns:
            int: Number of chunks deleted
        """
        # Count existing chunks first
        count_result = self.client.count(
            collection_name=self.collection_name,
            count_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="page_url",
                        match=models.MatchValue(value=page_path),
                    )
                ]
            ),
        )

        if count_result.count == 0:
            return 0

        # Delete chunks
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="page_url",
                            match=models.MatchValue(value=page_path),
                        )
                    ]
                )
            ),
        )

        return count_result.count

    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection (size, vector count, etc.)."""
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }
        except UnexpectedResponse:
            return {
                "name": self.collection_name,
                "vectors_count": 0,
                "points_count": 0,
                "status": "not_found",
            }


# Singleton instance
vector_store = VectorStoreService()
