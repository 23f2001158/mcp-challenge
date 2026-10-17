import asyncio
import hashlib
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

EMAIL = "23f2001158@ds.study.iitm.ac.in"
CHALLENGE = "0123456789abcdef0123456789abcdef"

async def main():
    url = "http://127.0.0.1:8000/mcp"

    async with streamablehttp_client(
        url,
        headers={"X-Exam-Challenge": CHALLENGE},
    ) as streams:
        read_stream, write_stream, _ = streams

        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            result = await session.call_tool("solve_challenge", {})
            print("Server response:", result.content)

            expected = hashlib.sha256(
                f"{CHALLENGE}:{EMAIL}".encode()
            ).hexdigest()[:16]

            print("Expected response:", expected)

asyncio.run(main())
