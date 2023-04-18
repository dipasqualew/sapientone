import json

from fastapi import Request
from langchain.callbacks import get_openai_callback


async def add_used_tokens(request: Request, call_next):
    if request.headers.get("X-Report-Used-Tokens"):
        with get_openai_callback() as cb:
            response = await call_next(request)

        tokens = {
            "total": cb.total_tokens,
            "prompt": cb.prompt_tokens,
            "completion": cb.completion_tokens,
            "cost": cb.total_cost,
        }

        response.headers["X-Used-Tokens"] = json.dumps(tokens)

    else:
        response = await call_next(request)

    return response
