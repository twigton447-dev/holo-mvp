from html.parser import HTMLParser
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
WHITEPAPER = ROOT / "frontend" / "whitepaper.html"
BENCHMARK = ROOT / "frontend" / "benchmark.html"
CONTACT_EMAIL = "taylorw@hologroup.io"
PHONE_NUMBER = "310-736-8232"


class _Parser(HTMLParser):
    pass


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_html_parses(path: Path) -> None:
    _Parser().feed(_read(path))


def test_public_pages_parse_as_html():
    _assert_html_parses(WHITEPAPER)
    _assert_html_parses(BENCHMARK)


def test_whitepaper_version_labels_stay_in_sync():
    html = _read(WHITEPAPER)
    versions = set(re.findall(r"Version ([0-9]+(?:\.[0-9]+)*)", html))
    assert versions == {"7.6"}


def test_benchmark_version_labels_stay_in_sync():
    html = _read(BENCHMARK)
    versions = set(re.findall(r"Version ([0-9]+(?:\.[0-9]+)*)", html))
    assert versions == {"6.9"}


def test_whitepaper_problem_section_keeps_boundary_analogy():
    html = _read(WHITEPAPER)
    required = [
        "High-stakes AI needs Customs and Border Protection, not pre-9/11 airport security.",
        "The current standard for AI action security is closer to pre-9/11 airport security",
        "High-stakes AI needs something closer to Customs and Border Protection.",
        "Does your story hold up?",
        "Does the paperwork match the cargo?",
    ]
    for phrase in required:
        assert phrase in html


def test_whitepaper_header_uses_public_links_and_email_contact():
    html = _read(WHITEPAPER)
    required = [
        "https://holoengine.ai",
        "https://holoengine.ai/benchmark",
        f"mailto:{CONTACT_EMAIL}",
        CONTACT_EMAIL,
    ]
    for phrase in required:
        assert phrase in html

    forbidden = [
        PHONE_NUMBER,
        "tel:+13107368232",
        "<span>Role</span>",
        "Founder, HoloEngine",
        "<span>Focus</span>",
        "Evidence before action",
    ]
    for phrase in forbidden:
        assert phrase not in html


def test_whitepaper_holobuild_lane_copy_is_locked():
    html = _read(WHITEPAPER)
    assert "<span>Early Lane</span>" in html
    assert "<h3>HoloBuild</h3>" in html
    assert "Creates high-stakes work that people can rely on." in html
    assert "Checks high-stakes work before people rely on it." not in html


def test_benchmark_and_whitepaper_contact_stay_aligned():
    whitepaper = _read(WHITEPAPER)
    benchmark = _read(BENCHMARK)

    assert CONTACT_EMAIL in whitepaper
    assert CONTACT_EMAIL in benchmark
    assert PHONE_NUMBER not in whitepaper
    assert PHONE_NUMBER not in benchmark
    assert "tel:+13107368232" not in whitepaper
    assert "tel:+13107368232" not in benchmark



def main() -> None:
    test_public_pages_parse_as_html()
    test_whitepaper_version_labels_stay_in_sync()
    test_benchmark_version_labels_stay_in_sync()
    test_whitepaper_problem_section_keeps_boundary_analogy()
    test_whitepaper_header_uses_public_links_and_email_contact()
    test_whitepaper_holobuild_lane_copy_is_locked()
    test_benchmark_and_whitepaper_contact_stay_aligned()
    print("PUBLIC_PAGES_CONTENT_LOCK_PASS")


if __name__ == "__main__":
    main()
