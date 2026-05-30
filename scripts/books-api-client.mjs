#!/usr/bin/env node

import { writeFile } from "node:fs/promises";

const DEFAULT_BASE_URL = "http://0.0.0.0:6180";
const QUERY_NAMES = ["q", "query", "search", "term", "text", "title", "author", "tag", "tags", "subject"];
const LIMIT_NAMES = ["limit", "page_size", "pageSize", "per_page", "perPage", "size", "count"];

function usage() {
  console.error(`Usage:
  node skills/calibre-ebooks/scripts/books-api-client.mjs docs
  node skills/calibre-ebooks/scripts/books-api-client.mjs openapi
  node skills/calibre-ebooks/scripts/books-api-client.mjs paths
  node skills/calibre-ebooks/scripts/books-api-client.mjs search "term" --limit 10
  node skills/calibre-ebooks/scripts/books-api-client.mjs book 123
  node skills/calibre-ebooks/scripts/books-api-client.mjs request GET /path --query key=value --body '{"x":1}'

Options:
  --base URL       Override BOOKS_API_URL or ${DEFAULT_BASE_URL}
  --query k=v      Add query parameter, repeatable
  --body JSON      JSON request body for request
  --limit N        Search result limit when the endpoint exposes a limit parameter
  --output PATH    Save binary or text response to a file for request
`);
}

function parseArgs(argv) {
  const positional = [];
  const options = { query: [] };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--base") options.base = argv[++i];
    else if (arg === "--query") options.query.push(argv[++i]);
    else if (arg === "--body") options.body = argv[++i];
    else if (arg === "--limit") options.limit = argv[++i];
    else if (arg === "--output") options.output = argv[++i];
    else if (arg === "--help" || arg === "-h") options.help = true;
    else positional.push(arg);
  }

  return { positional, options };
}

function baseUrl(options) {
  return String(options.base || process.env.BOOKS_API_URL || DEFAULT_BASE_URL).replace(/\/+$/, "");
}

function apiUrl(base, path, params = {}) {
  const url = new URL(path.startsWith("/") ? `${base}${path}` : path);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") url.searchParams.set(key, String(value));
  }
  return url;
}

async function fetchResponse(url, init = {}) {
  let response;
  try {
    response = await fetch(url, init);
  } catch (error) {
    throw new Error(`${init.method || "GET"} ${url} failed: ${error.message}`);
  }
  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(`${init.method || "GET"} ${url} failed: ${response.status} ${response.statusText}${text ? `\n${text}` : ""}`);
  }
  return response;
}

async function fetchJson(url, init = {}) {
  const response = await fetchResponse(url, init);
  return response.json();
}

async function getOpenApi(base) {
  return fetchJson(apiUrl(base, "/openapi.json"));
}

function operationParams(operation, location) {
  return (operation.parameters || []).filter((param) => !location || param.in === location);
}

function summarizePaths(openapi) {
  const rows = [];
  for (const [path, item] of Object.entries(openapi.paths || {})) {
    for (const [method, operation] of Object.entries(item)) {
      if (!["get", "post", "put", "patch", "delete"].includes(method)) continue;
      rows.push({
        method: method.toUpperCase(),
        path,
        operationId: operation.operationId || null,
        summary: operation.summary || null,
        query: operationParams(operation, "query").map((param) => param.name),
        pathParams: operationParams(operation, "path").map((param) => param.name),
      });
    }
  }
  return rows;
}

function scoreSearchCandidate(row) {
  const haystack = `${row.path} ${row.operationId || ""} ${row.summary || ""}`.toLowerCase();
  const queryHit = row.query.find((name) => QUERY_NAMES.includes(name));
  let score = 0;
  if (row.method === "GET") score += 2;
  if (queryHit) score += 5;
  if (haystack.includes("search")) score += 4;
  if (haystack.includes("book")) score += 2;
  if (haystack.includes("author") || haystack.includes("title") || haystack.includes("tag")) score += 1;
  if (row.pathParams.length) score -= 5;
  return score;
}

function findSearchCandidates(openapi) {
  return summarizePaths(openapi)
    .map((row) => ({ ...row, score: scoreSearchCandidate(row) }))
    .filter((row) => row.score > 0 && row.method === "GET")
    .sort((a, b) => b.score - a.score);
}

function findBookCandidates(openapi) {
  return summarizePaths(openapi)
    .filter((row) => row.method === "GET" && row.pathParams.length > 0)
    .map((row) => {
      const haystack = `${row.path} ${row.operationId || ""} ${row.summary || ""}`.toLowerCase();
      const idParam = row.pathParams.find((name) => /(^id$|book.*id|calibre.*id)/i.test(name)) || row.pathParams[0];
      let score = 0;
      if (haystack.includes("book")) score += 5;
      if (haystack.includes("format")) score += 1;
      if (/book.*id|calibre.*id/i.test(idParam)) score += 3;
      return { ...row, idParam, score };
    })
    .filter((row) => row.score > 0)
    .sort((a, b) => b.score - a.score);
}

function replacePathParam(path, name, value) {
  return path.replace(new RegExp(`\\{${name}\\}`, "g"), encodeURIComponent(String(value)));
}

function parseQueryPairs(pairs) {
  const params = {};
  for (const pair of pairs) {
    const index = pair.indexOf("=");
    if (index === -1) throw new Error(`Invalid --query value, expected key=value: ${pair}`);
    params[pair.slice(0, index)] = pair.slice(index + 1);
  }
  return params;
}

async function commandSearch(base, openapi, query, options) {
  const candidates = findSearchCandidates(openapi);
  const attempted = [];

  for (const candidate of candidates) {
    const queryName = candidate.query.find((name) => QUERY_NAMES.includes(name)) || candidate.query[0];
    if (!queryName) continue;

    const params = { [queryName]: query };
    const limitName = candidate.query.find((name) => LIMIT_NAMES.includes(name));
    if (limitName && options.limit) params[limitName] = options.limit;

    const url = apiUrl(base, candidate.path, params);
    attempted.push({ method: candidate.method, path: candidate.path, params });
    try {
      const data = await fetchJson(url);
      return { endpoint: { method: candidate.method, path: candidate.path }, params, data };
    } catch (error) {
      attempted[attempted.length - 1].error = error.message;
    }
  }

  throw new Error(`No usable search endpoint succeeded. Candidates:\n${JSON.stringify(attempted, null, 2)}`);
}

async function commandBook(base, openapi, id) {
  const candidates = findBookCandidates(openapi);
  const attempted = [];

  for (const candidate of candidates) {
    const path = replacePathParam(candidate.path, candidate.idParam, id);
    const url = apiUrl(base, path);
    attempted.push({ method: candidate.method, path });
    try {
      const data = await fetchJson(url);
      return { endpoint: { method: candidate.method, path: candidate.path }, id, data };
    } catch (error) {
      attempted[attempted.length - 1].error = error.message;
    }
  }

  throw new Error(`No usable book detail endpoint succeeded. Candidates:\n${JSON.stringify(attempted, null, 2)}`);
}

async function commandRequest(base, method, path, options) {
  const headers = {};
  const init = { method: method.toUpperCase(), headers };
  const params = parseQueryPairs(options.query);

  if (options.body !== undefined) {
    headers["content-type"] = "application/json";
    init.body = options.body;
  }

  const response = await fetchResponse(apiUrl(base, path, params), init);
  const contentType = response.headers.get("content-type") || "";

  if (options.output) {
    const buffer = Buffer.from(await response.arrayBuffer());
    await writeFile(options.output, buffer);
    return { output: options.output, bytes: buffer.length, contentType };
  }

  if (contentType.includes("application/json")) return response.json();
  return response.text();
}

async function main() {
  const { positional, options } = parseArgs(process.argv.slice(2));
  if (options.help || positional.length === 0) {
    usage();
    return options.help ? 0 : 2;
  }

  const [command, ...rest] = positional;
  const base = baseUrl(options);

  if (command === "docs") {
    console.log(JSON.stringify({
      swagger: `${base}/docs`,
      redoc: `${base}/redoc`,
      openapi: `${base}/openapi.json`,
    }, null, 2));
    return 0;
  }

  if (command === "openapi") {
    console.log(JSON.stringify(await getOpenApi(base), null, 2));
    return 0;
  }

  if (command === "paths") {
    console.log(JSON.stringify(summarizePaths(await getOpenApi(base)), null, 2));
    return 0;
  }

  if (command === "search") {
    const query = rest.join(" ").trim();
    if (!query) throw new Error("search requires a query");
    console.log(JSON.stringify(await commandSearch(base, await getOpenApi(base), query, options), null, 2));
    return 0;
  }

  if (command === "book") {
    const id = rest[0];
    if (!id) throw new Error("book requires an id");
    console.log(JSON.stringify(await commandBook(base, await getOpenApi(base), id), null, 2));
    return 0;
  }

  if (command === "request") {
    const [method, path] = rest;
    if (!method || !path) throw new Error("request requires METHOD and PATH");
    const result = await commandRequest(base, method, path, options);
    if (typeof result === "string") console.log(result);
    else console.log(JSON.stringify(result, null, 2));
    return 0;
  }

  throw new Error(`Unknown command: ${command}`);
}

main()
  .then((code) => {
    process.exitCode = code;
  })
  .catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
