import json
from typing import Any

from aiohttp.web_response import Response


def respond(data: Any, status_message: str = 'ok', status_code: int = 200) -> Response:
    text = json.dumps({'status': status_message, 'data': data}, default=str, ensure_ascii=False)

    return Response(text=text, status=status_code, content_type='application/json')
