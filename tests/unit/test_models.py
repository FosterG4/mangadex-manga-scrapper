"""
Unit tests for data models.
"""

import unittest
from src.mangadx.models import Manga, Chapter, Author, LocalizedString


class TestLocalizedString(unittest.TestCase):
    """Test cases for LocalizedString."""

    def test_get_existing_language(self):
        """Test getting existing language."""
        ls = LocalizedString(values={"en": "English", "ja": "Japanese"})
        self.assertEqual(ls.get("en"), "English")
        self.assertEqual(ls.get("ja"), "Japanese")

    def test_get_missing_language(self):
        """Test getting missing language returns default."""
        ls = LocalizedString(values={"en": "English"})
        self.assertEqual(ls.get("fr", "Default"), "Default")
        self.assertEqual(ls.get("fr"), "")

    def test_bracket_notation(self):
        """Test bracket notation access."""
        ls = LocalizedString(values={"en": "English"})
        self.assertEqual(ls["en"], "English")
        self.assertEqual(ls["fr"], "")


class TestManga(unittest.TestCase):
    """Test cases for Manga model."""

    def test_from_dict(self):
        """Test creating Manga from dictionary."""
        data = {
            "id": "test-id",
            "attributes": {
                "title": {"en": "Test Manga"},
                "altTitles": [{"ja": "テスト"}],
                "description": {"en": "Test description"},
                "status": "ongoing",
                "year": 2023,
                "contentRating": "safe",
                "tags": [],
                "availableTranslatedLanguages": ["en", "ja"],
            },
            "relationships": [],
        }

        manga = Manga.from_dict(data)
        
        self.assertEqual(manga.id, "test-id")
        self.assertEqual(manga.title.get("en"), "Test Manga")
        self.assertEqual(manga.status, "ongoing")
        self.assertEqual(manga.year, 2023)
        self.assertIn("en", manga.available_translated_languages)


class TestChapter(unittest.TestCase):
    """Test cases for Chapter model."""

    def test_from_dict(self):
        """Test creating Chapter from dictionary."""
        data = {
            "id": "chapter-id",
            "attributes": {
                "title": "Test Chapter",
                "volume": "1",
                "chapter": "1",
                "pages": 20,
                "translatedLanguage": "en",
            },
            "relationships": [],
        }

        chapter = Chapter.from_dict(data)
        
        self.assertEqual(chapter.id, "chapter-id")
        self.assertEqual(chapter.title, "Test Chapter")
        self.assertEqual(chapter.volume, "1")
        self.assertEqual(chapter.chapter, "1")
        self.assertEqual(chapter.pages, 20)
        self.assertEqual(chapter.translated_language, "en")


class TestAuthor(unittest.TestCase):
    """Test cases for Author model."""

    def test_from_dict(self):
        """Test creating Author from dictionary."""
        data = {
            "id": "author-id",
            "attributes": {
                "name": "Test Author",
                "biography": {"en": "Test bio"},
                "twitter": "https://twitter.com/test",
            },
        }

        author = Author.from_dict(data)
        
        self.assertEqual(author.id, "author-id")
        self.assertEqual(author.name, "Test Author")
        self.assertEqual(author.biography.get("en"), "Test bio")
        self.assertEqual(author.twitter, "https://twitter.com/test")


if __name__ == "__main__":
    unittest.main()
