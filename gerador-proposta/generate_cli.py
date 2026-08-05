#!/usr/bin/env python3
"""CLI headless: BRIEF.md + API key → PPTX (sem Streamlit)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from generator import build_livre_deck, fill_slots, load_named_token_catalog  # noqa: E402
from generator import paths as P  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Gera proposta PPTX a partir de um brief")
    p.add_argument("--brief", required=True, help="Arquivo .md/.txt com o conteúdo")
    p.add_argument("--api-key", default=os.environ.get("PROPOSAL_API_KEY", ""))
    p.add_argument("--provider", default=os.environ.get("PROPOSAL_PROVIDER", "openai"))
    p.add_argument("--model", default=os.environ.get("PROPOSAL_MODEL_NAME", "gpt-4.1-mini"))
    p.add_argument("--client", default="")
    p.add_argument("--code", default="")
    p.add_argument("--logo", default="")
    p.add_argument("--out", default="")
    p.add_argument("--base-url", default=os.environ.get("PROPOSAL_BASE_URL", ""))
    args = p.parse_args()

    if not args.api_key:
        sys.exit("Informe --api-key ou PROPOSAL_API_KEY")

    brief = Path(args.brief).read_text(encoding="utf-8")
    catalog = load_named_token_catalog()
    example = None
    if P.example_values_path().is_file():
        example = json.loads(P.example_values_path().read_text(encoding="utf-8")).get("vigia")

    values = fill_slots(
        provider=args.provider,
        api_key=args.api_key,
        brief=brief,
        catalog=catalog,
        model=args.model,
        example_values=example,
        project_code=args.code,
        client_name=args.client,
        base_url=args.base_url or None,
    )

    out = Path(args.out) if args.out else (
        P.output_dir() / f"{args.code or 'PROPOSTA'} - {date.today().isoformat()}.pptx"
    )
    logo = Path(args.logo) if args.logo else None
    build_livre_deck(
        values,
        output_path=out,
        logo_path=logo,
        client_name=args.client,
        project_code=args.code,
    )
    print(f"OK: {out} ({len(catalog)} tokens)")


if __name__ == "__main__":
    main()
