from unittest import TestCase

from pgvector.sqlalchemy import Vector

from app.models import EmbeddingModel


class EmbeddingModelMetadataTests(TestCase):
    def test_vector_has_yandex_embedding_dimension(self) -> None:
        vector_column = EmbeddingModel.__table__.columns["vector"]

        self.assertIsInstance(vector_column.type, Vector)
        self.assertEqual(vector_column.type.dim, 256)
