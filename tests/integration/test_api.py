"""
Integration tests for API client.

These tests make real API calls to MangaDx.
Run with caution to avoid rate limiting.
"""

import unittest
import os
from src.mangadx import MangaDxClient
from src.mangadx.exceptions import MangaDxException


class TestMangaDxAPI(unittest.TestCase):
    """Integration tests for MangaDx API."""

    @classmethod
    def setUpClass(cls):
        """Set up test client."""
        cls.client = MangaDxClient()

    @classmethod
    def tearDownClass(cls):
        """Clean up client."""
        cls.client.close()

    def test_ping(self):
        """Test API ping."""
        result = self.client.ping()
        self.assertTrue(result)

    def test_search_manga(self):
        """Test manga search."""
        results = self.client.manga.search(title="One Piece", limit=5)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check first result has expected attributes
        manga = results[0]
        self.assertIsNotNone(manga.id)
        self.assertIsNotNone(manga.title)

    def test_get_manga_by_id(self):
        """Test getting manga by ID."""
        # Search for a manga first
        results = self.client.manga.search(title="One Piece", limit=1)
        
        if results:
            manga_id = results[0].id
            manga = self.client.manga.get(manga_id)
            
            self.assertEqual(manga.id, manga_id)
            self.assertIsNotNone(manga.title)

    def test_get_manga_aggregate(self):
        """Test getting manga chapters aggregate."""
        # Search for a manga first
        results = self.client.manga.search(title="One Piece", limit=1)
        
        if results:
            manga_id = results[0].id
            volumes = self.client.manga.get_aggregate(
                manga_id,
                translated_language=["en"]
            )
            
            self.assertIsInstance(volumes, dict)

    def test_get_chapter_list(self):
        """Test getting chapter list."""
        chapters = self.client.chapter.list(
            limit=10,
            translated_language=["en"]
        )
        
        self.assertIsInstance(chapters, list)
        self.assertLessEqual(len(chapters), 10)

    def test_get_author_list(self):
        """Test getting author list."""
        authors = self.client.author.list(limit=5)
        
        self.assertIsInstance(authors, list)
        self.assertLessEqual(len(authors), 5)

    def test_get_cover_list(self):
        """Test getting cover list."""
        covers = self.client.cover.list(limit=5)
        
        self.assertIsInstance(covers, list)
        self.assertLessEqual(len(covers), 5)

    def test_get_scanlation_group_list(self):
        """Test getting scanlation group list."""
        groups = self.client.scanlation_group.list(limit=5)
        
        self.assertIsInstance(groups, list)
        self.assertLessEqual(len(groups), 5)

    def test_get_tag_list(self):
        """Test getting tag list."""
        tags = self.client.manga.get_tag_list()
        
        self.assertIsInstance(tags, list)
        self.assertGreater(len(tags), 0)


if __name__ == "__main__":
    # Only run if explicitly requested
    if os.getenv("RUN_INTEGRATION_TESTS") == "true":
        unittest.main()
    else:
        print("Skipping integration tests. Set RUN_INTEGRATION_TESTS=true to run.")
