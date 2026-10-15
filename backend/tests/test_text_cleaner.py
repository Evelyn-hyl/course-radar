from unittest import TestCase

from app.ingestion.text_cleaner import clean_extracted_text


class ExtractedTextCleanerTests(TestCase):
    def test_repairs_mojibake_and_normalizes_extraction_markup(self) -> None:
        dirty = (
            "## Diracâ€™s Theorem\r\n\r\n\r\n"
            "<!-- Start of picture text -->\n"
            "1 2 3<br>4 5 6\n"
            "<!-- End of picture text -->\n\n\n\n"
            "Weâ€™ll assume Î´(G) â©¾ n/2.   "
        )

        result = clean_extracted_text(dirty)

        self.assertEqual(
            result,
            (
                "## Dirac’s Theorem\n\n"
                "1 2 3\n"
                "4 5 6\n\n"
                "We’ll assume δ(G) ⩾ n/2."
            ),
        )

    def test_preserves_meaningful_markdown_and_inline_html(self) -> None:
        text = "**Result:** _G_<sup>′</sup> is Hamiltonian."

        self.assertEqual(clean_extracted_text(text), text)

    def test_removes_invisible_extraction_characters(self) -> None:
        text = "Hamil\u00adtonian\u200b cycle"

        self.assertEqual(clean_extracted_text(text), "Hamiltonian cycle")
