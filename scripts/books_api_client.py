#!/usr/bin/env python3
"""Books API client for the calibre-ebooks OpenClaw skill."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_OUTPUT_ROOT = SKILL_DIR / "tmp" / "downloads"
TMP_OUTPUT_ROOT = Path("/tmp/calibre-ebooks")
QUERY_NAMES = ["q", "query", "search", "term", "text", "title", "author", "tag", "tags", "subject"]
LIMIT_NAMES = ["limit", "page_size", "pageSize", "per_page", "perPage", "size", "count"]
DEFAULT_BASE_URL = "http://127.0.0.1:6180"


def env_candidates() -> list[Path]:
    return [
        SCRIPT_DIR / ".env",
        SKILL_DIR / ".env",
        Path.cwd() / ".env",
    ]


def parse_env_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if stripped.startswith("export "):
        stripped = stripped[len("export "):].lstrip()
    if "=" not in stripped:
        return None
    key, value = stripped.split("=", 1)
    key = key.strip()
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
        return None
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    else:
        value = re.sub(r"\s+#.*$", "", value).rstrip()
    return key, value


def load_env_files() -> None:
    seen: set[Path] = set()
    for candidate in env_candidates():
        env_file = candidate.resolve()
        if env_file in seen or not env_file.is_file():
            continue
        seen.add(env_file)
        for line in env_file.read_text(encoding="utf-8").splitlines():
            parsed = parse_env_line(line)
            if not parsed:
                continue
            key, value = parsed
            os.environ.setdefault(key, value)


def base_url(value: str | None) -> str:
    return (value or os.environ.get("BOOKS_API_URL") or DEFAULT_BASE_URL).rstrip("/")


def api_key() -> str | None:
    value = os.environ.get("BOOKS_API_KEY") or os.environ.get("API_KEY")
    if value and value.strip():
        return value.strip()
    return None


def api_url(base: str, path: str, params: dict[str, str] | None = None) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        raise ValueError("Full URLs are not allowed here; pass an API path such as /api/books")
    url = urljoin(f"{base}/", path.lstrip("/"))
    if not params:
        return url
    query = urlencode({key: value for key, value in params.items() if value not in (None, "")})
    return f"{url}{'&' if urlparse(url).query else '?'}{query}" if query else url


def request_bytes(url: str, method: str = "GET", body: str | None = None) -> tuple[bytes, dict[str, str]]:
    headers = {}
    token = api_key()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = body.encode("utf-8")
    request = Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urlopen(request) as response:
            return response.read(), {key.lower(): value for key, value in response.headers.items()}
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"{method.upper()} {urlparse(url).path} failed: {error.code} {error.reason}"
            f"{chr(10) + detail if detail else ''}"
        ) from error
    except URLError as error:
        raise RuntimeError(f"{method.upper()} {urlparse(url).path} failed: {error.reason}") from error


def request_json(url: str, method: str = "GET", body: str | None = None) -> Any:
    payload, _headers = request_bytes(url, method=method, body=body)
    return json.loads(payload.decode("utf-8"))


def get_openapi(base: str) -> Any:
    return request_json(api_url(base, "/openapi.json"))


def operation_params(operation: dict[str, Any], location: str | None = None) -> list[dict[str, Any]]:
    return [param for param in operation.get("parameters", []) if location is None or param.get("in") == location]


def summarize_paths(openapi: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for path, item in openapi.get("paths", {}).items():
        for method, operation in item.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            rows.append(
                {
                    "method": method.upper(),
                    "path": path,
                    "operationId": operation.get("operationId"),
                    "summary": operation.get("summary"),
                    "query": [param["name"] for param in operation_params(operation, "query")],
                    "pathParams": [param["name"] for param in operation_params(operation, "path")],
                }
            )
    return rows


def score_search_candidate(row: dict[str, Any]) -> int:
    haystack = f"{row['path']} {row.get('operationId') or ''} {row.get('summary') or ''}".lower()
    score = 0
    if row["method"] == "GET":
        score += 2
    if any(name in QUERY_NAMES for name in row["query"]):
        score += 5
    if "search" in haystack:
        score += 4
    if "book" in haystack:
        score += 2
    if any(word in haystack for word in ("author", "title", "tag")):
        score += 1
    if row["pathParams"]:
        score -= 5
    return score


def find_search_candidates(openapi: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in summarize_paths(openapi):
        scored = {**row, "score": score_search_candidate(row)}
        if scored["score"] > 0 and scored["method"] == "GET":
            rows.append(scored)
    return sorted(rows, key=lambda item: item["score"], reverse=True)


def find_book_candidates(openapi: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in summarize_paths(openapi):
        if row["method"] != "GET" or not row["pathParams"]:
            continue
        haystack = f"{row['path']} {row.get('operationId') or ''} {row.get('summary') or ''}".lower()
        id_param = next((name for name in row["pathParams"] if re.search(r"(^id$|book.*id|calibre.*id)", name, re.I)), row["pathParams"][0])
        score = 0
        if "book" in haystack:
            score += 5
        if "format" in haystack:
            score += 1
        if re.search(r"book.*id|calibre.*id", id_param, re.I):
            score += 3
        if score > 0:
            rows.append({**row, "idParam": id_param, "score": score})
    return sorted(rows, key=lambda item: item["score"], reverse=True)


def replace_path_param(path: str, name: str, value: str) -> str:
    return path.replace(f"{{{name}}}", quote(str(value), safe=""))


def parse_query_pairs(pairs: list[str]) -> dict[str, str]:
    params = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid --query value, expected key=value: {pair}")
        key, value = pair.split("=", 1)
        params[key] = value
    return params


def content_disposition_filename(header: str | None) -> str | None:
    if not header:
        return None
    encoded = re.search(r"filename\*=UTF-8''([^;]+)", header, re.I)
    if encoded:
        return quote(encoded.group(1).strip().strip('"'), safe="%").replace("%25", "%")
    plain = re.search(r'filename="?([^";]+)"?', header, re.I)
    return plain.group(1).strip() if plain else None


def safe_basename(name: str | None) -> str:
    cleaned = re.sub(r"[^\w .()+\-[\]]+", "_", name or "", flags=re.UNICODE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or "download"


def fallback_filename(path_value: str, headers: dict[str, str], content_type: str) -> str:
    from_header = content_disposition_filename(headers.get("content-disposition"))
    if from_header:
        return safe_basename(from_header)
    fmt = headers.get("x-book-format")
    extension_by_type = {
        "application/pdf": ".pdf",
        "application/epub+zip": ".epub",
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "text/markdown": ".md",
        "text/plain": ".txt",
    }
    extension = f".{fmt.lower()}" if fmt else extension_by_type.get(content_type.split(";")[0], "")
    base = "-".join(part for part in path_value.split("?")[0].split("/") if part)
    return safe_basename(f"{base or 'download'}{extension}")


def resolve_output_path(output: str | None, output_dir: str | None, request_path: str, headers: dict[str, str], content_type: str) -> Path | None:
    filename = fallback_filename(request_path, headers, content_type)
    if output_dir:
        output_dir_path = Path(output_dir)
        output_path = checked_output_path(output_dir_path / filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path
    if not output:
        return None
    output_path = Path(output)
    if output.endswith("/") or output_path.is_dir():
        output_path = checked_output_path(output_path / filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path
    output_path = checked_output_path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def checked_output_path(path: Path) -> Path:
    resolved = path.resolve()
    if os.environ.get("ALLOW_ARBITRARY_OUTPUT_PATH", "").lower() in {"1", "true", "yes", "s", "sim"}:
        return resolved
    allowed_roots = [DEFAULT_OUTPUT_ROOT.resolve(), TMP_OUTPUT_ROOT.resolve()]
    if any(resolved.is_relative_to(root) for root in allowed_roots):
        return resolved
    raise RuntimeError(
        "Refusing to write outside skills/calibre-ebooks/tmp/downloads or /tmp/calibre-ebooks. "
        "Set ALLOW_ARBITRARY_OUTPUT_PATH=true to override."
    )


def command_search(base: str, openapi: dict[str, Any], query: str, limit: str | None) -> dict[str, Any]:
    attempted = []
    for candidate in find_search_candidates(openapi):
        query_name = next((name for name in candidate["query"] if name in QUERY_NAMES), candidate["query"][0] if candidate["query"] else None)
        if not query_name:
            continue
        params = {query_name: query}
        limit_name = next((name for name in candidate["query"] if name in LIMIT_NAMES), None)
        if limit_name and limit:
            params[limit_name] = limit
        attempted.append({"method": candidate["method"], "path": candidate["path"], "params": params})
        try:
            data = request_json(api_url(base, candidate["path"], params))
            return {"endpoint": {"method": candidate["method"], "path": candidate["path"]}, "params": params, "data": data}
        except RuntimeError as error:
            attempted[-1]["error"] = str(error)
    raise RuntimeError(f"No usable search endpoint succeeded. Candidates:\n{json.dumps(attempted, ensure_ascii=False, indent=2)}")


def command_book(base: str, openapi: dict[str, Any], book_id: str) -> dict[str, Any]:
    attempted = []
    for candidate in find_book_candidates(openapi):
        path = replace_path_param(candidate["path"], candidate["idParam"], book_id)
        attempted.append({"method": candidate["method"], "path": path})
        try:
            data = request_json(api_url(base, path))
            return {"endpoint": {"method": candidate["method"], "path": candidate["path"]}, "id": book_id, "data": data}
        except RuntimeError as error:
            attempted[-1]["error"] = str(error)
    raise RuntimeError(f"No usable book detail endpoint succeeded. Candidates:\n{json.dumps(attempted, ensure_ascii=False, indent=2)}")


def command_request(base: str, method: str, path: str, args: argparse.Namespace) -> Any:
    parsed_path = urlparse(path)
    if parsed_path.scheme or parsed_path.netloc:
        raise RuntimeError("Full URLs are not allowed for request; pass a local /api/... path.")
    if not path.startswith("/api/"):
        raise RuntimeError("request is limited to /api/... paths.")
    if method != "GET" and os.environ.get("ALLOW_MUTATING_API_REQUESTS", "").lower() not in {"1", "true", "yes", "s", "sim"}:
        raise RuntimeError("Mutating API requests are disabled. Set ALLOW_MUTATING_API_REQUESTS=true to enable them.")
    if args.body and method == "GET":
        raise RuntimeError("GET requests cannot include --body.")
    params = parse_query_pairs(args.query)
    payload, headers = request_bytes(api_url(base, path, params), method=method, body=args.body)
    content_type = headers.get("content-type", "")
    output_path = resolve_output_path(args.output, args.output_dir, path, headers, content_type)
    if output_path:
        output_path.write_bytes(payload)
        return {"output": str(output_path), "bytes": len(payload), "contentType": content_type}
    if "application/json" in content_type:
        return json.loads(payload.decode("utf-8"))
    return payload.decode("utf-8", errors="replace")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Client for the local Calibre-backed Books API.",
        epilog=(
            "Examples:\n"
            "  books_api_client.py docs\n"
            "  books_api_client.py paths\n"
            "  books_api_client.py search \"python\" --limit 10\n"
            "  books_api_client.py book 123\n"
            "  books_api_client.py request GET /api/books --query limit=100\n"
            "  books_api_client.py request GET /api/books/123/file --output-dir tmp/downloads"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--base",
        metavar="URL",
        help=(
            "Books API base URL. Overrides BOOKS_API_URL and the default "
            f"{DEFAULT_BASE_URL}."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("docs", help="Print Swagger, ReDoc, and OpenAPI URLs for the selected API base.")
    sub.add_parser("openapi", help="Fetch and print the current OpenAPI JSON document.")
    sub.add_parser("paths", help="Print API paths, methods, operation IDs, and path/query parameters.")

    search = sub.add_parser(
        "search",
        help="Search books using the best matching GET endpoint discovered from OpenAPI.",
    )
    search.add_argument("query", help="Search text, such as a title, author, tag, subject, or free term.")
    search.add_argument(
        "--limit",
        metavar="N",
        help="Maximum number of results when the discovered endpoint exposes a supported limit parameter.",
    )

    book = sub.add_parser(
        "book",
        help="Fetch book details by ID using the best matching detail endpoint discovered from OpenAPI.",
    )
    book.add_argument("book_id", help="Book identifier accepted by the API path parameter.")

    request = sub.add_parser(
        "request",
        help="Call an explicit API endpoint after inspecting OpenAPI.",
    )
    request.add_argument(
        "method",
        type=str.upper,
        help="HTTP method to send. Non-GET methods require ALLOW_MUTATING_API_REQUESTS=true.",
    )
    request.add_argument(
        "path",
        help="Books API path such as /api/books. Full http(s) URLs are rejected.",
    )
    request.add_argument(
        "--query",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Query string pair. Repeat for multiple parameters.",
    )
    request.add_argument(
        "--body",
        metavar="JSON",
        help="Raw JSON request body. Content-Type is set to application/json.",
    )
    request.add_argument(
        "--output",
        metavar="PATH",
        help=(
            "Write a non-JSON or file response to this file or directory. "
            "If PATH ends with / or is an existing directory, the API filename is used. "
            "By default writes are limited to skills/calibre-ebooks/tmp/downloads or /tmp/calibre-ebooks."
        ),
    )
    request.add_argument(
        "--output-dir",
        metavar="DIR",
        help="Write the response into DIR using the API-provided filename or a safe fallback filename.",
    )
    return parser


def print_result(data: Any) -> None:
    if isinstance(data, str):
        print(data)
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


def main(argv: list[str]) -> int:
    load_env_files()
    args = build_parser().parse_args(argv)
    base = base_url(args.base)

    if args.command == "docs":
        print_result({"swagger": f"{base}/docs", "redoc": f"{base}/redoc", "openapi": f"{base}/openapi.json"})
    elif args.command == "openapi":
        print_result(get_openapi(base))
    elif args.command == "paths":
        print_result(summarize_paths(get_openapi(base)))
    elif args.command == "search":
        print_result(command_search(base, get_openapi(base), args.query, args.limit))
    elif args.command == "book":
        print_result(command_book(base, get_openapi(base), args.book_id))
    elif args.command == "request":
        print_result(command_request(base, args.method, args.path, args))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
