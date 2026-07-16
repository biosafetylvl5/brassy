"""Unit tests for _split_template_lines and generate_section_string."""

from brassy.actions.build_release_notes import (
    _split_template_lines,
    generate_section_string,
)
from brassy.brassy import Settings
from brassy.templates.settings_template import DefaultTemplate


def _get_entry_template_lines():
    """Return the default entry template lines."""
    for section in DefaultTemplate.release_template:
        for section_name, lines in section.items():
            if section_name == "entry":
                return lines
    return []


def _get_summary_template_lines():
    """Return the default summary template lines."""
    for section in DefaultTemplate.release_template:
        for section_name, lines in section.items():
            if section_name == "summary":
                return lines
    return []


def _make_files():
    """Return empty files dict used in changelog entries."""
    return {"deleted": [], "moved": [], "added": [], "modified": []}


class TestSplitTemplateLines:
    """Tests for _split_template_lines."""

    def test_splits_entry_template_at_title(self):
        """Entry template splits with {title} in entry_lines."""
        lines = _get_entry_template_lines()
        category_lines, entry_lines = _split_template_lines(lines)
        assert "{title}" not in "\n".join(category_lines)
        assert "{title}" in "\n".join(entry_lines)
        assert len(category_lines) > 0
        assert len(entry_lines) > 0

    def test_summary_template_all_entry(self):
        """Summary template returns empty category_lines."""
        lines = _get_summary_template_lines()
        category_lines, entry_lines = _split_template_lines(lines)
        assert category_lines == []
        assert entry_lines == lines

    def test_no_entry_keywords_all_category(self):
        """Lines with no entry keywords return all as category_lines."""
        lines = ["line one", "line two", "line three"]
        category_lines, entry_lines = _split_template_lines(lines)
        assert category_lines == lines
        assert entry_lines == []

    def test_change_type_only_in_category(self):
        """Lines with only {change_type} go to category_lines."""
        lines = ["", "{change_type}", "==="]
        category_lines, entry_lines = _split_template_lines(lines)
        assert category_lines == lines
        assert entry_lines == []


class TestGenerateSectionString:
    """Tests for generate_section_string."""

    def test_single_entry_per_category_unchanged(self):
        """Single entry renders heading once (not duplicated)."""
        lines = _get_entry_template_lines()
        entries = {
            "bug fix": [
                {
                    "title": "hello",
                    "description": "world",
                    "files": _make_files(),
                },
            ],
        }
        result = generate_section_string(
            lines, entries, "2024-01-01", "1.0", "ftr", "hdr",
        )
        assert result.count("Bug fix") == 1

    def test_multiple_entries_single_heading(self):
        """Multiple entries in one category share a single heading."""
        lines = _get_entry_template_lines()
        entries = {
            "bug fix": [
                {
                    "title": "fix a",
                    "description": "desc a",
                    "files": _make_files(),
                },
                {
                    "title": "fix b",
                    "description": "desc b",
                    "files": _make_files(),
                },
            ],
        }
        result = generate_section_string(
            lines, entries, "2024-01-01", "1.0", "ftr", "hdr",
        )
        assert result.count("Bug fix") == 1

    def test_multiple_categories_grouped(self):
        """Multiple categories each get their own heading once."""
        lines = _get_entry_template_lines()
        entries = {
            "bug fix": [
                {"title": "a", "description": "a", "files": _make_files()},
            ],
            "enhancement": [
                {"title": "b", "description": "b", "files": _make_files()},
            ],
        }
        result = generate_section_string(
            lines, entries, "2024-01-01", "1.0", "ftr", "hdr",
        )
        assert result.count("Bug fix") == 1
        assert result.count("Enhancement") == 1

    def test_empty_entries_skipped(self):
        """Category with only empty entries produces no heading."""
        lines = _get_entry_template_lines()
        entries = {
            "bug fix": [
                {
                    "title": "",
                    "description": "",
                    "files": _make_files(),
                },
            ],
        }
        result = generate_section_string(
            lines, entries, "2024-01-01", "1.0", "ftr", "hdr",
        )
        assert "Bug fix" not in result

    def test_mixed_valid_and_empty_entries(self):
        """Empty-only categories are skipped; valid ones render."""
        lines = _get_entry_template_lines()
        entries = {
            "bug fix": [
                {"title": "", "description": "", "files": _make_files()},
                {"title": "valid", "description": "desc", "files": _make_files()},
            ],
            "enhancement": [
                {"title": "", "description": "", "files": _make_files()},
            ],
        }
        result = generate_section_string(
            lines, entries, "2024-01-01", "1.0", "ftr", "hdr",
        )
        assert "Bug fix" in result
        assert "Enhancement" not in result

    def test_summary_template_per_entry(self):
        """Summary template still renders per entry (no category heading)."""
        lines = _get_summary_template_lines()
        entries = {
            "bug fix": [
                {"title": "fix a", "description": "desc a", "files": _make_files()},
                {"title": "fix b", "description": "desc b", "files": _make_files()},
            ],
        }
        result = generate_section_string(
            lines, entries, "2024-01-01", "1.0", "ftr", "hdr",
        )
        assert "Fix a" in result
        assert "Fix b" in result

    def test_default_title_and_description_fallbacks(self):
        """Missing title or description uses Settings defaults."""
        lines = _get_entry_template_lines()
        entries = {
            "bug fix": [
                {
                    "title": "",
                    "description": "has description, no title",
                    "files": _make_files(),
                },
                {
                    "title": "real title",
                    "description": "",
                    "files": _make_files(),
                },
            ],
        }
        result = generate_section_string(
            lines, entries, "2024-01-01", "1.0", "ftr", "hdr",
        )
        assert Settings.default_title in result
        assert Settings.default_description in result

    def test_inter_entry_blank_line(self):
        """Multi-entry category inserts blank line between entries."""
        lines = _get_entry_template_lines()
        entries = {
            "bug fix": [
                {"title": "fix a", "description": "desc a", "files": _make_files()},
                {"title": "fix b", "description": "desc b", "files": _make_files()},
            ],
        }
        result = generate_section_string(
            lines, entries, "2024-01-01", "1.0", "ftr", "hdr",
        )
        assert "\n\nFix b" in result

    def test_file_change_rendering(self):
        """Entry with file changes includes them in output."""
        lines = _get_entry_template_lines()
        entries = {
            "bug fix": [
                {
                    "title": "fix",
                    "description": "desc",
                    "files": {
                        "deleted": [],
                        "moved": [],
                        "added": ["new_file.py"],
                        "modified": [],
                    },
                },
            ],
        }
        result = generate_section_string(
            lines, entries, "2024-01-01", "1.0", "ftr", "hdr",
        )
        assert "added: new_file.py" in result

    def test_header_footer_version_date_substitution(self):
        """Post-processing substitutes header, footer, version, and date."""
        lines = ["{prefix_file}", "{suffix_file}", "{release_version}", "{release_date}"]
        entries = {}
        result = generate_section_string(
            lines, entries, "2025-06-01", "2.0", "footer_text", "header_text",
        )
        assert "header_text" in result
        assert "footer_text" in result
        assert "2.0" in result
        assert "2025-06-01" in result
