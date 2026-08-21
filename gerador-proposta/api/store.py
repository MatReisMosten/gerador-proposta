"""Store efêmero em memória para o binário do PPTX gerado.

Decisão da Fase 2 (ver docs/plano-migracao-react.md): nada é persistido em
disco compartilhado — o arquivo vive só até o download (ou até expirar) e
depois some. Resolve dois problemas do Fase 1: histórico visível entre
usuários e colisão de arquivo quando duas gerações usam o mesmo código de
projeto ao mesmo tempo.

Limitação assumida: store em memória de processo único. Se o deploy rodar
com mais de um worker uvicorn/gunicorn, isso precisa virar Redis (ou
equivalente) — não é um problema neste estágio (uso interno, baixo volume).
"""

from __future__ import annotations

import secrets
import threading
import time
from dataclasses import dataclass

from . import config


@dataclass
class StoredProposal:
    filename: str
    content: bytes
    meta: dict
    expires_at: float


class ProposalStore:
    def __init__(self, ttl_seconds: int = config.DOWNLOAD_TTL_SECONDS) -> None:
        self._ttl = ttl_seconds
        self._items: dict[str, StoredProposal] = {}
        self._lock = threading.Lock()

    def put(self, *, filename: str, content: bytes, meta: dict) -> str:
        self._sweep()
        token = secrets.token_urlsafe(24)
        with self._lock:
            self._items[token] = StoredProposal(
                filename=filename,
                content=content,
                meta=meta,
                expires_at=time.time() + self._ttl,
            )
        return token

    def get(self, token: str) -> StoredProposal | None:
        with self._lock:
            item = self._items.get(token)
            if item is None:
                return None
            if item.expires_at < time.time():
                del self._items[token]
                return None
            return item

    def _sweep(self) -> None:
        now = time.time()
        with self._lock:
            expired = [k for k, v in self._items.items() if v.expires_at < now]
            for k in expired:
                del self._items[k]


store = ProposalStore()
