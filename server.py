
import hashlib

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

EMAIL = "23f2001158@ds.study.iitm.ac.in"
latest_challenge = ""

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
    """Return the hash for the current exam challenge."""
    challenge = latest_challenge

    if len(challenge) != 32:
        raise ValueError("Invalid or missing X-Exam-Challenge header")

    message = f"{challenge}:{EMAIL.strip().lower()}".encode("utf-8")
    result = hashlib.sha256(message).hexdigest()[:16]

    print(f"Challenge received: {challenge!r}")
    print(f"Hash returned: {result}")

    return result


class ChallengeHeaderMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        global latest_challenge

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        challenge = headers.get(
            b"x-exam-challenge", b""
        ).decode("ascii", errors="ignore")

        if scope.get("path") == "/mcp" and scope.get("method") == "POST":
            latest_challenge = challenge
            print(f"HTTP challenge: {challenge!r}")

        await self.app(scope, receive, send)


app = ChallengeHeaderMiddleware(mcp.streamable_http_app())
