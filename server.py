
import hashlib

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.transport_security import TransportSecuritySettings

EMAIL = "23f2001158@ds.study.iitm.ac.in"

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
def solve_challenge(ctx: Context) -> str:
    """Return the required hash for the current exam challenge."""
    headers = ctx.headers or {}
    challenge = headers.get("x-exam-challenge", "")

    if not challenge:
        raise ValueError("Missing X-Exam-Challenge header")

    message = f"{challenge}:{EMAIL.strip().lower()}".encode("utf-8")
    return hashlib.sha256(message).hexdigest()[:16]


app = mcp.streamable_http_app()
