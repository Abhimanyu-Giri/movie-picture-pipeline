#!/usr/bin/env python3
"""Verify public AWS endpoints and save measured evidence, never sample proof."""
import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen


def aws_url(value):
    value = value.rstrip("/")
    parsed = urlsplit(value)
    if (
        parsed.scheme != "http"
        or not re.fullmatch(
            r"[a-zA-Z0-9.-]+\.elb\.(?:amazonaws\.com|[a-z0-9-]+\.amazonaws\.com)",
            parsed.hostname or "",
        )
        or parsed.netloc != parsed.hostname
        or parsed.path
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Expected the HTTP root URL of this project's AWS LoadBalancer")
    return value


def fetch(url, origin=None):
    headers = {"User-Agent": "movie-picture-pipeline-runtime-check"}
    if origin:
        headers["Origin"] = origin
    for attempt in range(12):
        try:
            with urlopen(Request(url, headers=headers), timeout=15) as response:
                if response.status != 200:
                    raise ValueError(f"Expected HTTP 200 from {url}; got {response.status}")
                return response.read(), dict(response.headers.items())
        except (HTTPError, URLError, TimeoutError, ConnectionError):
            if attempt == 11:
                raise
            time.sleep(5)


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            source = dict(attrs).get("src")
            if source:
                self.sources.append(source)


def verify(backend, frontend, output):
    backend = aws_url(backend)
    frontend = aws_url(frontend) if frontend else None
    output.mkdir(parents=True, exist_ok=True)
    # A failed rerun must not leave an old success report in this directory.
    for name in ("checks.json", "ENDPOINTS.md", "movies.json", "api-headers.json", "frontend.html"):
        (output / name).unlink(missing_ok=True)
    body, headers = fetch(backend + "/movies", origin=frontend)
    data = json.loads(body)
    if not isinstance(data, dict):
        raise ValueError("The /movies response is not a JSON object")
    movies = data.get("movies")
    if not isinstance(movies, list) or not movies:
        raise ValueError("The /movies response has no movie list")
    if any(not isinstance(movie, dict) or not movie.get("title") for movie in movies):
        raise ValueError("A movie is missing its title")
    checks = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "backend_url": backend,
        "backend_movies_status": 200,
        "movie_count": len(movies),
    }
    if frontend:
        cors = {k.lower(): v for k, v in headers.items()}.get("access-control-allow-origin")
        if cors not in ("*", frontend):
            raise ValueError("The backend does not allow the frontend origin through CORS")
        html, _ = fetch(frontend)
        parser = Scripts()
        parser.feed(html.decode("utf-8"))
        found = False
        for source in parser.sources:
            script_url = urljoin(frontend + "/", source)
            if urlsplit(script_url).netloc != urlsplit(frontend).netloc:
                continue
            bundle, _ = fetch(script_url)
            if backend.encode() in bundle:
                found = True
                break
        if not found:
            raise ValueError("The served frontend JavaScript does not contain the actual backend URL; rebuild frontend CD")
        (output / "frontend.html").write_bytes(html)
        checks.update(frontend_url=frontend, frontend_status=200,
                      backend_url_found_in_served_javascript=True, cors_allowed=True)
    (output / "movies.json").write_text(json.dumps(data, indent=2) + "\n")
    (output / "api-headers.json").write_text(json.dumps(headers, indent=2) + "\n")
    (output / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    lines = ["# Verified AWS runtime endpoints", "", f"Checked: {checks['checked_at_utc']}", "",
             f"- Backend API: {backend}/movies"]
    if frontend:
        lines += [f"- Frontend: {frontend}", "- The served JavaScript contains the backend URL; CORS passed."]
    lines += [f"- Backend returned HTTP 200 with {len(movies)} movies.", "",
              "These are HTTP and bundle checks. Add browser screenshots showing the rendered movie list."]
    (output / "ENDPOINTS.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--frontend")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    verify(args.backend, args.frontend, args.output)
