"""Erros de domínio da geração — viram HTTP 422 com mensagem em PT-BR."""

from __future__ import annotations


class GenerationError(Exception):
    """Erro esperado de validação/geração — mensagem já pronta para o usuário."""
