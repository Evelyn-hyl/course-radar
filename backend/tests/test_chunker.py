from pathlib import Path
from typing import TypedDict
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from app.ingestion.chunker import PdfChunkingError, chunk_pdf


class PageMetadata(TypedDict):
    page_number: int


class PageChunkFixture(TypedDict):
    text: str
    metadata: PageMetadata


PAGE_CHUNK: PageChunkFixture = {
    "text": "  Bayes' rule relates conditional probabilities.  ",
    "metadata": {"page_number": 2},
}

class PdfChunkerTests(TestCase):
    def test_normalizes_pymupdf4llm_chunks(self) -> None:
        with TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "sample.pdf"
            pdf_path.write_bytes(b"%PDF-test")

            with patch(
                "app.ingestion.chunker.pymupdf4llm.to_markdown",
                return_value=[PAGE_CHUNK],
            ) as to_markdown:
                result = chunk_pdf(pdf_path)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "Bayes' rule relates conditional probabilities.")
        self.assertEqual((result[0].page_start, result[0].page_end), (2, 2))
        self.assertEqual(result[0].section_path, ())
        to_markdown.assert_called_once_with(
            pdf_path,
            page_chunks=True,
            show_progress=False,
        )

    def test_missing_file_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            chunk_pdf(Path("does-not-exist.pdf"))

    def test_empty_extraction_raises_chunking_error(self) -> None:
        with TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "empty.pdf"
            pdf_path.write_bytes(b"%PDF-test")

            with patch(
                "app.ingestion.chunker.pymupdf4llm.to_markdown",
                return_value=[],
            ):
                with self.assertRaises(PdfChunkingError):
                    chunk_pdf(pdf_path)
