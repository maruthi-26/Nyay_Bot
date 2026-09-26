import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import chunk_text, parse_allowed_origins
from rag_engine import (
    AskRequest,
    DocumentChunk,
    EmbedRequest,
    MAX_STORED_DOCUMENTS,
    _chunk_stores,
    store_chunks,
)
from risk_engine import SummaryCardRequest


class ChunkingTests(unittest.TestCase):
    def test_chunking_advances_with_early_punctuation(self):
        text = "." + ("x" * 1500)

        chunks = chunk_text(text)

        self.assertGreater(len(chunks), 1)
        self.assertLessEqual(len(chunks), 4)
        starts = [chunk["start_char"] for chunk in chunks]
        self.assertEqual(starts, sorted(set(starts)))
        self.assertTrue(all(chunk["end_char"] <= len(text) for chunk in chunks))
        self.assertTrue(all(len(chunk["text"]) <= 600 for chunk in chunks))

    def test_render_hostname_is_normalized_for_cors(self):
        self.assertEqual(
            parse_allowed_origins("nyaybot-front-ot8e.onrender.com"),
            ["https://nyaybot-front-ot8e.onrender.com"],
        )

    def test_cors_wildcard_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_allowed_origins("*")


class RequestValidationTests(unittest.TestCase):
    def test_question_size_is_bounded(self):
        with self.assertRaises(ValueError):
            AskRequest(doc_id="document", question="x" * 2001)

    def test_language_code_is_validated(self):
        with self.assertRaises(ValueError):
            AskRequest(doc_id="document", question="question", language="xx")

    def test_chunk_payload_is_bounded(self):
        chunk = DocumentChunk(
            chunk_id="chunk_001",
            text="text",
            start_char=0,
            end_char=4,
        )
        with self.assertRaises(ValueError):
            EmbedRequest(doc_id="document", chunks=[chunk] * 501)

    def test_individual_chunk_text_is_bounded(self):
        with self.assertRaises(ValueError):
            DocumentChunk(
                chunk_id="chunk_001",
                text="x" * 601,
                start_char=0,
                end_char=601,
            )

    def test_memory_cache_evicts_oldest_document(self):
        chunk = DocumentChunk(
            chunk_id="chunk_001",
            text="text",
            start_char=0,
            end_char=4,
        )
        _chunk_stores.clear()

        for index in range(MAX_STORED_DOCUMENTS + 1):
            store_chunks(f"document-{index}", [chunk])

        self.assertEqual(len(_chunk_stores), MAX_STORED_DOCUMENTS)
        self.assertNotIn("document-0", _chunk_stores)
        self.assertIn(f"document-{MAX_STORED_DOCUMENTS}", _chunk_stores)

    def test_summary_card_payload_size_is_bounded(self):
        with self.assertRaises(ValueError):
            SummaryCardRequest(
                doc_id="document",
                analysis_result={"document_type": "x" * 20_001},
            )


if __name__ == "__main__":
    unittest.main()
