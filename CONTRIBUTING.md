# Contributing to MangaDex Manga Downloader

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of Python and REST APIs

### Setting Up Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/mangadex-manga-scrapper.git
   cd mangadex-manga-scrapper
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Copy environment file**
   ```bash
   cp .env.example .env
   ```

5. **Run tests**
   ```bash
   python -m unittest discover tests/unit
   ```

## Development Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions/updates

### Making Changes

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the code style guidelines
   - Add tests for new features
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run unit tests
   python -m unittest discover tests/unit
   
   # Run specific test
   python -m unittest tests.unit.test_http_client
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Go to GitHub and create a PR
   - Describe your changes clearly
   - Reference any related issues

## Code Style Guidelines

### Python Style

Follow PEP 8 with these specifics:

- **Indentation**: 4 spaces
- **Line length**: 100 characters (soft limit)
- **Imports**: Organized (standard library, third-party, local)
- **Type hints**: Use for function signatures
- **Docstrings**: Google style for all public functions/classes

### Example

```python
from typing import Optional, List
from pathlib import Path

def download_chapter(
    chapter_id: str,
    manga_title: str,
    volume: Optional[str] = None,
    chapter_number: str = "1",
) -> Path:
    """
    Download a single chapter.
    
    Args:
        chapter_id: Chapter UUID
        manga_title: Manga title for folder naming
        volume: Volume number (optional)
        chapter_number: Chapter number
    
    Returns:
        Path to downloaded chapter directory
    
    Raises:
        DownloadException: If download fails
    """
    # Implementation
    pass
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `MangaDexClient`)
- **Functions/Methods**: `snake_case` (e.g., `download_manga`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **Private**: Prefix with `_` (e.g., `_sanitize_filename`)

## Testing Guidelines

### Writing Tests

- **Unit tests**: Test individual functions/methods
- **Integration tests**: Test API interactions (optional)
- **Test coverage**: Aim for >80% coverage

### Test Structure

```python
import unittest
from src.mangadex import MangaDexClient

class TestMangaDexClient(unittest.TestCase):
    """Test MangaDex client functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = MangaDexClient()
    
    def tearDown(self):
        """Clean up after tests."""
        self.client.close()
    
    def test_ping(self):
        """Test API ping."""
        result = self.client.ping()
        self.assertTrue(result)
```

### Running Tests

```bash
# All unit tests
python -m unittest discover tests/unit

# Specific test file
python -m unittest tests.unit.test_http_client

# Specific test case
python -m unittest tests.unit.test_http_client.TestHTTPClient.test_get

# With coverage
coverage run -m unittest discover tests/unit
coverage report
```

## Documentation Guidelines

### Code Documentation

- **All public functions**: Must have docstrings
- **Complex logic**: Add inline comments
- **Type hints**: Required for function signatures

### Documentation Files

- **README.md**: Overview and quick start
- **docs/API_REFERENCE.md**: Complete API documentation
- **docs/USAGE_EXAMPLES.md**: Usage examples
- **CHANGELOG.md**: Version history

### Updating Documentation

When adding features:
1. Update relevant documentation files
2. Add usage examples
3. Update CHANGELOG.md

## Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

### Examples

```bash
feat(downloader): add automatic volume structure updates

- Detects volume assignment changes from API
- Automatically reorganizes chapters
- Cleans up empty folders

Closes #123

fix(http): handle rate limit retry-after header

The HTTP client now properly respects the retry-after
header when receiving 429 responses.

docs(readme): update installation instructions

Added virtual environment setup steps.
```

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Code follows style guidelines
```

## Issue Guidelines

### Bug Reports

Include:
- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/logs

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Additional context

## Project Structure

```
mangadex-manga-scrapper/
├── config/              # Configuration management
├── src/
│   ├── mangadex/       # Core API client
│   │   ├── api/        # API endpoint modules
│   │   ├── client.py   # Main client
│   │   ├── downloader.py  # Download manager
│   │   └── ...
│   └── utils/          # Utility modules
├── tests/              # Test suite
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── docs/               # Documentation
├── main.py             # CLI entry point
└── requirements.txt    # Dependencies
```

## Adding New Features

### API Endpoints

1. Add method to appropriate API module in `src/mangadex/api/`
2. Add model if needed in `src/mangadex/models.py`
3. Add tests in `tests/unit/`
4. Update documentation

### CLI Commands

1. Add command to `src/cli.py`
2. Update main menu
3. Add tests
4. Update documentation

## Code Review Process

1. **Automated checks**: CI runs tests and linters
2. **Manual review**: Maintainer reviews code
3. **Feedback**: Address review comments
4. **Approval**: Maintainer approves PR
5. **Merge**: PR merged to main branch

## Getting Help

- **Questions**: Open a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Documentation**: Check docs/ folder

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Copyright (c) 2025 thorryuk

All contributions become part of the project under the MIT License terms.

## Recognition

Contributors will be acknowledged in:
- README.md
- CHANGELOG.md
- GitHub contributors page

Thank you for contributing! 🎉
