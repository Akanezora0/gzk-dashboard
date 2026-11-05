"""GET-only bridge to the unchanged local low-altitude service.

Install before the LLM SPA catch-all route. The supplied web_root must be the
independent low-altitude bundle, not the original 5173 build directory.
"""
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener

from fastapi import FastAPI, HTTPException, Request as WebRequest
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles


ALLOWED = frozenset({'overview', 'tech/tree', 'survey', 'chain', 'contribution'})


def install_low_altitude(app: FastAPI, web_root: Path) -> None:
    @app.get('/api/low-altitude/{api_path:path}')
    def low_altitude_api(api_path: str, request: WebRequest):
        if api_path not in ALLOWED and not re.fullmatch(r'tech/[A-Za-z0-9_.-]+', api_path):
            raise HTTPException(404, '未知低空接口')
        query = request.url.query
        if len(query) > 2000:
            raise HTTPException(400, '查询参数过长')
        upstream = 'http://127.0.0.1:8080/api/' + api_path + ('?' + query if query else '')
        try:
            # The target is fixed; ambient external proxy settings are ignored.
            opener = build_opener(ProxyHandler({}))
            with opener.open(Request(upstream, headers={'Accept': 'application/json'}), timeout=20) as result:
                body = result.read(8 * 1024 * 1024 + 1)
                if len(body) > 8 * 1024 * 1024:
                    raise HTTPException(502, '低空数据响应过大')
                return Response(content=body, status_code=result.status, media_type='application/json')
        except HTTPError as exc:
            raise HTTPException(502, '低空数据接口暂不可用') from exc
        except (URLError, TimeoutError) as exc:
            raise HTTPException(503, '低空数据接口暂不可用') from exc

    app.mount('/low-altitude', StaticFiles(directory=web_root, html=True, check_dir=False), name='low-altitude')
