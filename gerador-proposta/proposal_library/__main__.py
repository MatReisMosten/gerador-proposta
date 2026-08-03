"""CLI entrypoint: python -m proposal_library <command> ..."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .import_ppt import default_staging_dir, import_ppt
from .apply_enrichment import apply_enrichment
from .utils import find_vault_root, resolve_path, setup_logging


def _add_import_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "import_ppt",
        help="Extrai slides de um PPTX para staging (sem IA)",
    )
    p.add_argument("pptx", help="Caminho do arquivo .pptx")
    p.add_argument(
        "--out",
        help="Diretório de staging (default: library/_staging/<batch_id>)",
    )
    p.add_argument(
        "--library",
        default=None,
        help="Raiz da library (default: <vault>/library)",
    )
    p.add_argument(
        "--skip-preview",
        action="store_true",
        help="Não gerar PNG (apenas para debug; não use em produção)",
    )


def _add_apply_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "apply_enrichment",
        help="Aplica enrichment JSON e grava slides na library",
    )
    p.add_argument("staging", help="Diretório de staging gerado por import_ppt")
    p.add_argument(
        "--library",
        default=None,
        help="Raiz da library (default: <vault>/library)",
    )
    p.add_argument(
        "--replace",
        action="append",
        default=[],
        metavar="SLIDE=ID",
        help="Substituir slide existente, ex: --replace 3=problem_001",
    )
    p.add_argument(
        "--skip",
        action="append",
        default=[],
        type=int,
        metavar="N",
        help="Ignorar número do slide (1-based)",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Ignorar detecção de duplicidade",
    )
    p.add_argument(
        "--keep-staging",
        action="store_true",
        default=True,
        help="Manter staging após apply (default)",
    )


def _default_library() -> Path:
    return find_vault_root() / "library"


def _parse_replace(items: list[str]) -> dict[int, str]:
    mapping: dict[int, str] = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"--replace inválido: {item!r} (use SLIDE=ID)")
        left, right = item.split("=", 1)
        mapping[int(left)] = right.strip()
    return mapping


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="proposal_library",
        description="Proposal Library Builder — extração e aplicação de enrichment",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)
    _add_import_parser(sub)
    _add_apply_parser(sub)

    args = parser.parse_args(argv)
    logger = setup_logging(level=10 if args.verbose else 20)

    if args.command == "import_ppt":
        library = resolve_path(args.library) if args.library else _default_library()
        out = resolve_path(args.out) if args.out else default_staging_dir(library)
        staging = import_ppt(
            Path(args.pptx),
            out,
            skip_preview=args.skip_preview,
        )
        print(json.dumps({"status": "ok", "staging": str(staging)}, ensure_ascii=False))
        return 0

    if args.command == "apply_enrichment":
        library = resolve_path(args.library) if args.library else _default_library()
        results = apply_enrichment(
            Path(args.staging),
            library,
            replace=_parse_replace(args.replace),
            skip_slides=set(args.skip or []),
            force=args.force,
            keep_staging=args.keep_staging,
        )
        payload = {
            "status": "ok",
            "results": [r.to_dict() for r in results],
            "needs_decision": [
                r.to_dict() for r in results if r.status == "needs_decision"
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if any(r.status == "error" for r in results):
            return 2
        if any(r.status == "needs_decision" for r in results):
            return 3
        return 0

    parser.error(f"Comando desconhecido: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
