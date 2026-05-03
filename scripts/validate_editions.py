#!/usr/bin/env python3
"""Validate CsR News daily edition JSON files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


PRIMARY_CATEGORIES = {
    "enterprise",
    "backend",
    "design",
    "distarch",
    "fundamentals",
    "integ",
    "devops",
    "data",
}

SECONDARY_CATEGORIES = {"obs", "frontend", "cloud", "testing"}
OTHER_CATEGORIES = {"ai", "aiops", "sec", "fintech"}

VALID_CATEGORIES = PRIMARY_CATEGORIES | SECONDARY_CATEGORIES | OTHER_CATEGORIES

TOOL_KEYS = {
    "claudecode",
    "cursor",
    "intellij",
    "vscode",
    "argocd",
    "ghactions",
    "github",
    "docker",
    "kubernetes",
    "terraform",
    "istio",
    "nginx",
    "databricks",
    "postgres",
    "redis",
    "kafka",
    "dynatrace",
    "datadog",
    "keycloak",
    "secrets-manager",
    "gradle",
    "maven",
    "springboot",
    "structurizr",
    "plantuml",
    "mermaid",
    "java",
    "javascript",
    "python",
    "mongodb",
    "angular",
    "react",
    "spring",
    "rabbitmq",
    "sns",
    "sqs",
    "checkmarx",
    "sonar",
}

VALID_KINDS = {"release", "news", "tutorial", "tip", "curiosity"}
IMAGE_REQUIRED_TOOL_KINDS = {"release", "news", "tutorial"}

ROOT_REQUIRED = {
    "date",
    "weekday",
    "formatted_date",
    "generated_at",
    "hero_title",
    "hero_description",
    "edition_digest",
    "highlights",
    "news",
    "tools",
    "videos",
}

NEWS_REQUIRED = {
    "category",
    "category_label",
    "category_icon",
    "headline",
    "summary",
    "explain",
    "source_key",
    "url",
    "read_time",
    "image",
}

TOOL_REQUIRED = {"tool_key", "name", "kind", "headline", "explain", "source_key", "url"}
EXPLAIN_REQUIRED = {"junior", "pleno", "senior"}
CLICKBAIT_RE = re.compile(
    r"\b(top\s*\d+|\d+\s+(razoes|razões|ways|things)|melhores\s+\d+|voce nao vai acreditar|você não vai acreditar)\b",
    re.IGNORECASE,
)
FALLBACK_IMAGE_RE = re.compile(
    r"google\.com/s2/favicons|simpleicons\.org|favicon|cropped-favicon|apple-touch-icon"
    r"|screenshot\.11ty\.dev|screenshotapi|urlbox|thum\.io",
    re.IGNORECASE,
)
CVE_RE = re.compile(r"^CVE-\d{4}-\d{4,}$")
GENERIC_PATHS = {
    "",
    "/",
    "/blog",
    "/blog/",
    "/news",
    "/news/",
    "/releases",
    "/releases/",
    "/changelog",
    "/changelog/",
    "/about-aws/whats-new",
    "/about-aws/whats-new/",
}


class Reporter:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_source_keys(repo_root: Path) -> set[str]:
    sources_path = repo_root / "data" / "sources.json"
    if not sources_path.exists():
        return set()
    try:
        data = load_json(sources_path)
    except Exception:
        return set()
    if not isinstance(data, dict):
        return set()
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        return set()
    return {s.get("key") for s in sources if isinstance(s, dict) and isinstance(s.get("key"), str)}


def is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_https_url(value: object) -> bool:
    return isinstance(value, str) and value.startswith("https://") and len(value) > 12


def domain(url: object) -> str:
    if not isinstance(url, str):
        return ""
    return urlparse(url).netloc.lower().removeprefix("www.")


def is_generic_url(url: object) -> bool:
    if not isinstance(url, str):
        return True
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    if parsed.path in GENERIC_PATHS or path in {p.rstrip("/") for p in GENERIC_PATHS}:
        return True
    if path.endswith("/blog") or path.endswith("/news") or path.endswith("/releases"):
        return True
    return False


def word_count(text: object) -> int:
    if not isinstance(text, str):
        return 0
    return len(re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE))


def validate_explain(reporter: Reporter, explain: object, label: str) -> None:
    if not isinstance(explain, dict):
        reporter.error(f"{label}: explain must be an object")
        return
    for key in EXPLAIN_REQUIRED:
        if not is_nonempty_string(explain.get(key)):
            reporter.error(f"{label}: explain.{key} is required")
    glossary = explain.get("glossary", [])
    if glossary is not None and not isinstance(glossary, list):
        reporter.error(f"{label}: explain.glossary must be an array when present")


def validate_common_story(
    reporter: Reporter,
    item: object,
    label: str,
    source_keys: set[str],
    require_image: bool,
    image_no_fallback: bool,
) -> None:
    if not isinstance(item, dict):
        reporter.error(f"{label}: item must be an object")
        return

    if not is_https_url(item.get("url")):
        reporter.error(f"{label}: url must be a non-empty https:// URL")
    elif is_generic_url(item.get("url")):
        reporter.error(f"{label}: url is too generic: {item.get('url')}")

    if source_keys and item.get("source_key") not in source_keys:
        reporter.error(f"{label}: unknown source_key {item.get('source_key')!r}")

    if require_image:
        image = item.get("image")
        if not is_https_url(image):
            reporter.error(f"{label}: image must be a non-empty https:// URL")
        elif image_no_fallback and FALLBACK_IMAGE_RE.search(image):
            reporter.error(f"{label}: image uses blocked fallback: {image}")

    validate_explain(reporter, item.get("explain"), label)

    for text_key in ("headline", "summary", "description"):
        value = item.get(text_key)
        if isinstance(value, str) and CLICKBAIT_RE.search(value):
            reporter.error(f"{label}: clickbait pattern in {text_key}")


def validate_news_item(reporter: Reporter, item: object, index: int, source_keys: set[str]) -> None:
    label = f"news[{index}]"
    if not isinstance(item, dict):
        reporter.error(f"{label}: item must be an object")
        return
    missing = sorted(k for k in NEWS_REQUIRED if k not in item)
    if missing:
        reporter.error(f"{label}: missing required fields: {', '.join(missing)}")

    category = item.get("category")
    if category not in VALID_CATEGORIES:
        reporter.error(f"{label}: invalid category {category!r}")
    if not isinstance(item.get("read_time"), int) or item.get("read_time", 0) <= 0:
        reporter.error(f"{label}: read_time must be a positive integer")
    if item.get("category") == "sec" and item.get("urgent") is True and not item.get("severity"):
        reporter.error(f"{label}: urgent security item requires severity")
    for cve in item.get("cves", []) or []:
        if not isinstance(cve, str) or not CVE_RE.match(cve):
            reporter.error(f"{label}: invalid CVE format {cve!r}")

    validate_common_story(reporter, item, label, source_keys, require_image=True, image_no_fallback=True)


def validate_tool_item(reporter: Reporter, item: object, index: int, source_keys: set[str]) -> None:
    label = f"tools[{index}]"
    if not isinstance(item, dict):
        reporter.error(f"{label}: item must be an object")
        return
    missing = sorted(k for k in TOOL_REQUIRED if k not in item)
    if missing:
        reporter.error(f"{label}: missing required fields: {', '.join(missing)}")

    tool_key = item.get("tool_key")
    kind = item.get("kind")
    if tool_key not in TOOL_KEYS:
        reporter.error(f"{label}: invalid tool_key {tool_key!r}")
    if kind not in VALID_KINDS:
        reporter.error(f"{label}: invalid kind {kind!r}")
    if kind == "release" and not is_nonempty_string(item.get("version")):
        reporter.error(f"{label}: release item requires version")

    if "category" in item and item.get("category") not in VALID_CATEGORIES:
        reporter.error(f"{label}: invalid category {item.get('category')!r}")

    require_image = kind in IMAGE_REQUIRED_TOOL_KINDS
    validate_common_story(
        reporter,
        item,
        label,
        source_keys,
        require_image=require_image,
        image_no_fallback=require_image,
    )


def validate_video_item(reporter: Reporter, item: object, index: int) -> None:
    label = f"videos[{index}]"
    if not isinstance(item, dict):
        reporter.error(f"{label}: item must be an object")
        return
    if "start" in item:
        reporter.error(f"{label}: start field must not exist")
    for key in ("id", "url", "title", "channel"):
        if not is_nonempty_string(item.get(key)):
            reporter.error(f"{label}: {key} is required")
    if is_nonempty_string(item.get("url")) and not item["url"].startswith("https://www.youtube.com/watch?v="):
        reporter.warn(f"{label}: expected canonical YouTube watch URL")


def category_group(category: object) -> str:
    if category in PRIMARY_CATEGORIES:
        return "primary"
    if category in SECONDARY_CATEGORIES:
        return "secondary"
    if category in OTHER_CATEGORIES:
        return "other"
    return "invalid"


def validate_editorial_profile(reporter: Reporter, data: dict) -> None:
    news = [item for item in data.get("news", []) if isinstance(item, dict)]
    highlights = [item for item in data.get("highlights", []) if isinstance(item, dict)]

    if not news:
        return

    groups = Counter(category_group(item.get("category")) for item in news)
    total = len(news)
    primary_ratio = groups["primary"] / total
    secondary_ratio = groups["secondary"] / total
    other_ratio = groups["other"] / total

    if primary_ratio < 0.40:
        reporter.warn(f"news[] primary category ratio is low: {primary_ratio:.0%} (target 50-60%)")
    if secondary_ratio < 0.15:
        reporter.warn(f"news[] secondary category ratio is low: {secondary_ratio:.0%} (target 25-35%)")
    if other_ratio > 0.20:
        reporter.warn(f"news[] other category ratio is high: {other_ratio:.0%} (target <=20%)")

    preferred_candidates = [
        item
        for item in [*news, *[t for t in data.get("tools", []) if isinstance(t, dict)]]
        if category_group(item.get("category")) in {"primary", "secondary"}
    ]
    highlight_other_count = sum(1 for item in highlights if category_group(item.get("category")) == "other")
    if preferred_candidates and highlights:
        first_group = category_group(highlights[0].get("category"))
        if first_group == "other":
            reporter.error("first highlight is from ai/aiops/sec/fintech while preferred candidates exist")
        if highlight_other_count > 1:
            reporter.error("more than one highlight is from ai/aiops/sec/fintech while preferred candidates exist")


def validate_edition(path: Path, repo_root: Path, warnings_as_errors: bool) -> int:
    reporter = Reporter()
    source_keys = load_source_keys(repo_root)

    try:
        data = load_json(path)
    except Exception as exc:
        print(f"{path}: ERROR: cannot read JSON: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print(f"{path}: ERROR: root must be an object", file=sys.stderr)
        return 1

    missing_root = sorted(k for k in ROOT_REQUIRED if k not in data)
    if missing_root:
        reporter.error(f"root: missing required fields: {', '.join(missing_root)}")

    if path.stem != data.get("date"):
        reporter.warn(f"root: file name {path.stem!r} does not match date {data.get('date')!r}")

    for key in ("hero_title", "hero_description", "edition_digest"):
        if not is_nonempty_string(data.get(key)):
            reporter.error(f"root: {key} is required")

    digest_words = word_count(data.get("edition_digest"))
    if digest_words and not (180 <= digest_words <= 380):
        reporter.warn(f"root: edition_digest has {digest_words} words (target 200-350)")

    news = data.get("news", [])
    tools = data.get("tools", [])
    highlights = data.get("highlights", [])
    videos = data.get("videos", [])
    for key, value in (("news", news), ("tools", tools), ("highlights", highlights), ("videos", videos)):
        if not isinstance(value, list):
            reporter.error(f"root: {key} must be an array")

    if isinstance(news, list) and len(news) < 15:
        reporter.error(f"news[]: expected at least 15 items, found {len(news)}")
    if isinstance(tools, list) and len(tools) < 10:
        reporter.error(f"tools[]: expected at least 10 items, found {len(tools)}")
    if isinstance(highlights, list) and len(highlights) != 3:
        reporter.error(f"highlights[]: expected exactly 3 items, found {len(highlights)}")
    if isinstance(videos, list) and len(videos) != 3:
        reporter.error(f"videos[]: expected exactly 3 items, found {len(videos)}")

    if isinstance(news, list):
        for index, item in enumerate(news):
            validate_news_item(reporter, item, index, source_keys)
    if isinstance(tools, list):
        for index, item in enumerate(tools):
            validate_tool_item(reporter, item, index, source_keys)
    if isinstance(highlights, list):
        for index, item in enumerate(highlights):
            label = f"highlights[{index}]"
            if not isinstance(item, dict):
                reporter.error(f"{label}: item must be an object")
                continue
            if item.get("source_array") not in {"news", "tools"}:
                reporter.error(f"{label}: source_array must be 'news' or 'tools'")
            if item.get("category") not in VALID_CATEGORIES:
                reporter.error(f"{label}: invalid category {item.get('category')!r}")
            validate_common_story(reporter, item, label, source_keys, require_image=True, image_no_fallback=True)
    if isinstance(videos, list):
        for index, item in enumerate(videos):
            validate_video_item(reporter, item, index)

    if isinstance(news, list) and isinstance(highlights, list):
        validate_editorial_profile(reporter, data)

    news_urls = []
    if isinstance(news, list):
        news_urls.extend(item.get("url") for item in news if isinstance(item, dict))
    tool_urls = []
    if isinstance(tools, list):
        tool_urls.extend(item.get("url") for item in tools if isinstance(item, dict))
    for label, section_urls in (("news[]", news_urls), ("tools[]", tool_urls)):
        duplicates = [url for url, count in Counter(section_urls).items() if url and count > 1]
        for url in duplicates:
            reporter.error(f"duplicate URL inside {label}: {url}")
    cross_section_duplicates = sorted(set(news_urls) & set(tool_urls))
    for url in cross_section_duplicates:
        reporter.warn(f"URL appears in both news[] and tools[]: {url}")

    urls = [*news_urls, *tool_urls]
    domains = Counter(domain(url) for url in urls if domain(url))
    for host, count in domains.items():
        if count > 3:
            reporter.warn(f"domain appears {count} times: {host}")

    for warning in reporter.warnings:
        print(f"{path}: WARNING: {warning}", file=sys.stderr)
    for error in reporter.errors:
        print(f"{path}: ERROR: {error}", file=sys.stderr)

    if reporter.errors or (warnings_as_errors and reporter.warnings):
        return 1
    print(f"{path}: OK ({len(reporter.warnings)} warnings)")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate CsR News daily edition JSON files.")
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--warnings-as-errors", action="store_true")
    args = parser.parse_args(argv)

    status = 0
    for path in args.files:
        status |= validate_edition(path, args.repo_root, args.warnings_as_errors)
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
