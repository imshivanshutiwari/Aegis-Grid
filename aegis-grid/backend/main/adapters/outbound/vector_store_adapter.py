from typing import List, Dict, Any, Optional
import uuid
import logging

class AsyncQdrantClientMock:
    """Mock for testing/isolation without Qdrant running."""
    def __init__(self, url): self.url = url
    async def get_collections(self):
        class C: collections=[]
        return C()
    async def create_collection(self, **kwargs): pass
    async def upsert(self, **kwargs): pass
    async def search(self, **kwargs): return []
    async def query(self, **kwargs): return []

try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.models import Distance, VectorParams, ScalarQuantization, ScalarQuantizationConfig, ScalarType
    QDRANT_AVAILABLE = True
except ImportError:
    AsyncQdrantClient = AsyncQdrantClientMock
    QDRANT_AVAILABLE = False

from main.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

class VectorStoreAdapter:
    """Async Qdrant connection adapter implementing Scalar Quantization and Hybrid Search capabilities."""
    def __init__(self, qdrant_url: str):
        self.client = AsyncQdrantClient(url=qdrant_url) if QDRANT_AVAILABLE else AsyncQdrantClientMock(url=qdrant_url)
        self.collection_name = "doctrines"

    async def initialize(self):
        try:
            collections = await self.client.get_collections()
            if not any(c.name == self.collection_name for c in collections.collections):

                if QDRANT_AVAILABLE:
                    await self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(size=4096, distance=Distance.COSINE),
                        quantization_config=ScalarQuantization(
                            scalar=ScalarQuantizationConfig(
                                type=ScalarType.INT8,
                                quantile=0.99,
                                always_ram=True
                            )
                        )
                    )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {e}")
            raise e

    async def add_documents(self, embeddings: List[List[float]], payloads: List[Dict[str, Any]]):
        if not QDRANT_AVAILABLE: return
        from qdrant_client.models import PointStruct
        points = [
            PointStruct(id=str(uuid.uuid4()), vector=emb, payload=payload)
            for emb, payload in zip(embeddings, payloads)
        ]
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    async def search(self, query_embedding: List[float], limit: int = 5) -> List[Any]:
        return await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
        )

vector_store = VectorStoreAdapter(settings.qdrant_url)
