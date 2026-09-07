"""Same-origin HTTP boundary for the local coordinator."""

from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from pb_stats.auth import SAFE_METHODS, LocalAuth
from pb_stats.contracts import ConflictDetail, ConflictResponse, RenameWorkspace, Workspace
from pb_stats.store import RevisionConflict, Store


def create_app(
    database: Path,
    static_dir: Path,
    session_token: str,
    port: int = 8765,
    *,
    store: Store | None = None,
) -> FastAPI:
    if not session_token:
        raise ValueError("A launcher session credential is required")
    auth = LocalAuth(port=port, session_token=session_token)
    active_store = store if store is not None else Store(database)
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def protect_local_session(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if not auth.verify_host(request.headers.get("host")):
            return JSONResponse({"detail": "Invalid local host"}, status_code=400)
        supplied_origin = request.headers.get("origin")
        if not auth.allows_origin(supplied_origin):
            return JSONResponse({"detail": "Invalid local origin"}, status_code=403)
        path = request.url.path
        if path == "/api" or path.startswith("/api/"):
            token = request.headers.get("x-session-token", "")
            if not auth.verify_token(token):
                return JSONResponse({"detail": "Local session required"}, status_code=401)
            if request.method not in SAFE_METHODS and not auth.allows_mutation_origin(
                supplied_origin
            ):
                return JSONResponse({"detail": "Mutation requires local origin"}, status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; script-src 'self'; "
            "connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'"
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/api/workspace")
    def read_workspace() -> Workspace:
        return active_store.read_workspace()

    @app.patch(
        "/api/workspace", response_model=Workspace, responses={409: {"model": ConflictResponse}}
    )
    def rename_workspace(proposal: RenameWorkspace) -> Workspace | JSONResponse:
        try:
            return active_store.rename_workspace(proposal.name, proposal.expected_revision)
        except RevisionConflict as error:
            conflict = ConflictResponse(
                detail=ConflictDetail(
                    message="Workspace changed; review the latest revision before retrying.",
                    current_revision=error.revision,
                )
            )
            return JSONResponse(conflict.model_dump(), status_code=409)

    # API misses must never resolve to the browser shell.
    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def missing_api(path: str) -> JSONResponse:
        return JSONResponse({"detail": "Not found"}, status_code=404)

    app.mount("/", StaticFiles(directory=static_dir, html=True), name="ui")
    return app
