"""Loopback-only session credential and origin checks for the local coordinator."""

from __future__ import annotations

import secrets
from dataclasses import dataclass

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


@dataclass(frozen=True)
class LocalAuth:
    """Per-launch credential plus the loopback authority it is bound to."""

    port: int
    session_token: str

    def __post_init__(self) -> None:
        if not self.session_token:
            raise ValueError("A launcher session credential is required")

    @property
    def authority(self) -> str:
        return f"127.0.0.1:{self.port}"

    @property
    def origin(self) -> str:
        return f"http://{self.authority}"

    def verify_host(self, host: str | None) -> bool:
        return host is not None and host.lower() == self.authority.lower()

    def allows_origin(self, supplied_origin: str | None) -> bool:
        return supplied_origin is None or supplied_origin == self.origin

    def allows_mutation_origin(self, supplied_origin: str | None) -> bool:
        return supplied_origin == self.origin

    def verify_token(self, token: str) -> bool:
        return secrets.compare_digest(token.encode("utf-8"), self.session_token.encode("utf-8"))
