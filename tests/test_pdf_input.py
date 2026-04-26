import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from studybot import StudyBot


class TestPDFInput(unittest.TestCase):

    def _make_bot(self, **kwargs):
        # Patch load_documents so no real file I/O is needed
        with patch.object(StudyBot, "load_documents", return_value=[]):
            return StudyBot(**kwargs)

    def test_pdf_path_stored_on_instance(self):
        """StudyBot stores the provided pdf_path at self.pdf_path."""
        bot = self._make_bot(pdf_path="notes.pdf")
        self.assertEqual(bot.pdf_path, "notes.pdf")

    def test_pdf_path_defaults_to_none(self):
        """pdf_path defaults to None when not provided."""
        bot = self._make_bot()
        self.assertIsNone(bot.pdf_path)

    def test_pdf_path_preserves_full_path(self):
        """StudyBot stores the full path exactly as given."""
        full_path = "/home/user/study/biology_notes.pdf"
        bot = self._make_bot(pdf_path=full_path)
        self.assertEqual(bot.pdf_path, full_path)


if __name__ == "__main__":
    unittest.main()
