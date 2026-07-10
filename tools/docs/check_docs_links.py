#!/usr/bin/env python3
"""
TicketVision Platform - Documentation Link Checker

This script checks all links in the documentation to ensure they're valid.
Used in CI/CD pipeline to maintain documentation quality.
"""

import asyncio
import re
import sys
from pathlib import Path
from types import TracebackType
from typing import Any

import httpx


class LinkChecker:
    """Asynchronous link checker for documentation."""

    def __init__(self, base_path: Path, _seconds_timeout: int = 10) -> None:
        """Initialize the link checker.

        Args:
            base_path: Base directory to scan for documentation files
            timeout: HTTP request seconds_timeout in seconds
        """
        self.base_path = base_path
        self.timeout = httpx.Timeout(read=10, write=10, connect=10, pool=10)
        self.session: httpx.AsyncClient | None = None
        self.checked_urls: set[str] = set()
        self.broken_links: list[tuple[str, str, str]] = []

    async def __aenter__(self) -> "LinkChecker":
        """Async context manager entry."""
        self.session = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()

    def find_markdown_files(self) -> list[Path]:
        """Find all markdown files in the documentation directory.

        Returns:
            List of Path objects for markdown files
        """
        markdown_files: list[Path] = []

        # Scan docs directory
        docs_dir = self.base_path / "docs"
        if docs_dir.exists():
            markdown_files.extend(docs_dir.rglob("*.md"))

        # Include root markdown files
        for md_file in self.base_path.glob("*.md"):
            markdown_files.append(md_file)

        return sorted(markdown_files)

    def extract_links(self, file_path: Path) -> list[tuple[str, int]]:
        """Extract all links from a markdown file.

        Args:
            file_path: Path to the markdown file

        Returns:
            List of tuples containing (url, line_number)
        """
        links = []

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Regex patterns for different link types
            patterns = [
                # Markdown links: [text](url)
                r"\[([^\]]+)\]\(([^)]+)\)",
                # Reference links: [text]: url
                r"^\s*\[([^\]]+)\]:\s*(.+)$",
                # HTML links: <a href="url">
                r'<a\s+[^>]*href=["\']([^"\']+)["\']',
                # Direct URLs: http://example.com
                r"https?://[^\s\])+",
                # Relative links in HTML: href="./path"
                r'href=["\']([^"\']+)["\']',
            ]

            for line_num, line in enumerate(lines, 1):
                for pattern in patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        # Extract URL from different capture groups
                        if len(match.groups()) >= 2:
                            url = match.group(2).strip()
                        else:
                            url = match.group(1).strip()

                        # Skip empty URLs, anchors, and email links
                        if (
                            url
                            and not url.startswith("#")
                            and not url.startswith("mailto:")
                        ):
                            links.append((url, line_num))

        except Exception:
            pass

        return links

    @staticmethod
    def is_external_url(url: str) -> bool:
        """Check if URL is external (http/https).

        Args:
            url: URL to check

        Returns:
            True if URL is external, False otherwise
        """
        return url.startswith(("http://", "https://"))

    @staticmethod
    def resolve_relative_path(file_path: Path, relative_url: str) -> Path:
        """Resolve relative path from markdown file location.

        Args:
            file_path: Path of the markdown file containing the link
            relative_url: Relative URL to resolve

        Returns:
            Resolved absolute path
        """
        # Remove anchors from URL
        clean_url = relative_url.split("#")[0].split("?")[0]

        if not clean_url:
            return file_path  # Empty path, link to same file

        # Resolve relative to the file's directory
        base_dir = file_path.parent
        return (base_dir / clean_url).resolve()

    async def check_external_url(self, url: str) -> bool:
        """Check if external URL is accessible.

        Args:
            url: External URL to check

        Returns:
            True if URL is accessible, False otherwise
        """
        if not self.session:
            return False

        try:
            # Skip already checked URLs
            if url in self.checked_urls:
                return True

            self.checked_urls.add(url)

            response = await self.session.head(url, follow_redirects=True)
            return response.status_code < 400

        except TimeoutError:
            return False
        except Exception:
            return False

    def check_internal_path(self, file_path: Path, relative_url: str) -> bool:
        """Check if internal file path exists.

        Args:
            file_path: Source markdown file path
            relative_url: Relative URL to check

        Returns:
            True if path exists, False otherwise
        """
        try:
            resolved_path = self.resolve_relative_path(file_path, relative_url)

            # Check if file exists
            if resolved_path.is_file():
                return True

            # Check if directory exists
            if resolved_path.is_dir():
                # Look for index files
                for index_file in ["index.md", "README.md", "index.html"]:
                    if (resolved_path / index_file).exists():
                        return True
                return True  # Directory exists

            return False

        except Exception as e:
            print(f"Error checking internal path: {e}")
            return False

    async def check_file_links(self, file_path: Path) -> None:
        """Check all links in a single file.

        Args:
            file_path: Path to the markdown file
        """

        links = self.extract_links(file_path)

        for url, line_num in links:
            if self.is_external_url(url):
                # Check external URL
                is_valid = await self.check_external_url(url)
                if not is_valid:
                    self.broken_links.append((str(file_path), str(line_num), url))
                else:
                    pass
            else:
                # Check internal path
                is_valid = self.check_internal_path(file_path, url)
                if not is_valid:
                    self.broken_links.append((str(file_path), str(line_num), url))
                else:
                    pass

    async def check_all_links(self) -> dict[str, Any]:
        """Check links in all documentation files.

        Returns:
            Dictionary with check results
        """
        markdown_files = self.find_markdown_files()

        if not markdown_files:
            return {"total_files": 0, "broken_links": 0, "success": True}

        # Check all files
        for file_path in markdown_files:
            await self.check_file_links(file_path)

        # Summary
        total_broken = len(self.broken_links)
        success = total_broken == 0

        if self.broken_links:
            for broken_file, _line_num, _url in self.broken_links:
                Path(broken_file).relative_to(self.base_path)

        return {
            "total_files": len(markdown_files),
            "broken_links": total_broken,
            "success": success,
            "broken_link_details": self.broken_links,
        }


async def main() -> None:
    """Main function to run the link checker."""
    base_path = Path.cwd()

    async with LinkChecker(base_path) as checker:
        results = await checker.check_all_links()

        if not results["success"]:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    # Install required packages if not available
    try:
        import httpx
    except ImportError:
        sys.exit(1)

    asyncio.run(main())
