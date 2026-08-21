"""Modelos Pydantic — contrato de API (ver docs/plano-migracao-react.md)."""

from __future__ import annotations

from pydantic import BaseModel


class ProposalTypeField(BaseModel):
    id: str
    label: str
    type: str = "text"
    placeholder: str = ""
    required: bool = False
    options: list[str] | None = None


class ProposalType(BaseModel):
    id: str
    label: str
    mode: str
    description: str = ""
    fields: list[ProposalTypeField] = []
    requires_form: bool
    show_brief: bool
    show_attachments: bool
    hide_client: bool = False
    hide_logo: bool = False


class LoginRequest(BaseModel):
    password: str = ""


class AuthStatus(BaseModel):
    authenticated: bool
    password_required: bool


class TemplateSummary(BaseModel):
    name: str
    size_label: str
    updated_at: str
    sections: dict[str, int]
    tokens: list[str]


class ExtractTextResponse(BaseModel):
    text: str
    truncated: bool


class ProposalMeta(BaseModel):
    client: str = ""
    code: str = ""
    type: str
    type_label: str
    size_label: str
    filename: str
    empty_tokens: int = 0


class GenerateProposalResponse(BaseModel):
    token: str
    meta: ProposalMeta


class ErrorResponse(BaseModel):
    detail: str
