#!/usr/bin/env python3
"""A local stand-in for an OpenAI-compatible chat endpoint, for smoke tests.

Replies come from a lookup table, not a model.

    python3 benchmark/mockserver.py --port 8931
"""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

CANNED = (
    "Sure! Here's what I found:\n\n"
    "# Overview\n\n"
    "- **First** point that runs on\n"
    "- Second point\n\n"
    "Let me know if you have any questions!"
)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802 - name fixed by BaseHTTPRequestHandler
        length = int(self.headers.get("content-length", 0))
        try:
            request = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            request = {}

        body = json.dumps(
            {
                "id": "mock",
                "object": "chat.completion",
                "model": request.get("model", "mock"),
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": CANNED},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
            }
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        return  # stay quiet inside make output


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8931)
    args = ap.parse_args()
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    print(f"mock chat endpoint listening on http://127.0.0.1:{args.port}/v1")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
