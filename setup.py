"""
Setup script for MangaDx Scrapper package.
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text(encoding="utf-8").strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="mangadx-scrapper",
    version="1.0.0",
    author="MangaDx Scrapper Team",
    author_email="",
    description="A Python library and CLI tool for downloading manga from MangaDx",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mangadx/mangadx-scrapper",
    packages=find_packages(exclude=["tests*", "docs*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mangadx-scrapper=mangadx_scrapper.cli.main:main",
            "mangadx-search=mangadx_scrapper.cli.search:search_command",
            "mangadx-download=mangadx_scrapper.cli.download:download_command",
        ],
    },
    include_package_data=True,
    package_data={
        "mangadx_scrapper": ["py.typed"],
    },
    keywords=[
        "manga",
        "mangadx",
        "download",
        "scraper",
        "api",
        "cli",
        "comics",
        "webtoon",
    ],
    project_urls={
        "Bug Reports": "https://github.com/mangadx/mangadx-scrapper/issues",
        "Source": "https://github.com/mangadx/mangadx-scrapper",
        "Documentation": "https://github.com/mangadx/mangadx-scrapper/blob/main/README.md",
    },
)
