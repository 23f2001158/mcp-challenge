
import hashlib
from contextvars import ContextVar

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

EMAIL = "23f2001158@ds.study.iitm.ac.in"
challenge_header = ContextVar("challenge_header", default="")

mcp = FastMCP(
    "Exam Challenge Server",
    transport_security=TransportSecuritySettings(
        allowed_hosts=[
            "mcp-challenge-ag3r.onrender.com",
            "mcp-challenge-ag3r.onrender.com:*",
        ],
    ),
)


@mcp.tool()
def solve_challenge() -> str:
    """Return the required hash for the current exam challenge."""
    challenge = challenge_header.get()

    if not challenge:
        raise ValueError("Missing X-Exam-Challenge header")

    message = f"{challenge}:{EMAIL}".encode("utf-8")
    return hashlib.sha256(message).hexdigest()[:16]


class ChallengeHeaderMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        challenge = headers.get(
            b"x-exam-challenge", b""
        ).decode("ascii", errors="ignore")

        token = challenge_header.set(challenge)
        try:
            await self.app(scope, receive, send)
        finally:
            challenge_header.reset(token)


app = ChallengeHeaderMiddleware(mcp.streamable_http_app())
